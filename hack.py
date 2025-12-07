import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import ctypes
from datetime import datetime

# -------- JSON DATA YOU PROVIDED --------
data = {
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Patient",
        "id": "p-101",
        "name": [{"text": "Mrs. Gupta"}],
        "gender": "female",
        "age": 65
      }
    },
    {
      "resource": {
        "resourceType": "Condition",
        "code": {
          "coding": [
            {
              "system": "http://snomed.info/sct",
              "code": "404640003",
              "display": "Dizziness"
            }
          ]
        },
        "clinicalStatus": "active"
      }
    },
    {
      "resource": {
        "resourceType": "Observation",
        "code": {
          "coding": [{
            "system": "http://snomed.info/sct",
            "code": "75367002",
            "display": "Blood Pressure"
          }]
        },
        "valueQuantity": {
          "value": 160,
          "unit": "mmHg/systolic"
        }
      }
    },
    {
      "resource": {
        "resourceType": "MedicationRequest",
        "status": "active",
        "intent": "order",
        "medicationCodeableConcept": {
          "coding": [
            {
              "system": "http://snomed.info/sct",
              "code": "386864001",
              "display": "Amlodipine 5mg Tablet"
            }
          ]
        },
        "dosageInstruction": [{
          "text": "1 tablet daily after food",
          "timing": {"code": "OD"}
        }]
      }
    }
  ]
}
# ----------------------------------------


# Extract relevant fields ----------------
patient = data["entry"][0]["resource"]
condition = data["entry"][1]["resource"]
bp = data["entry"][2]["resource"]
med = data["entry"][3]["resource"]

patient_name = patient["name"][0]["text"]
gender = patient["gender"].capitalize()
age = patient["age"]

diagnosis = condition["code"]["coding"][0]["display"]
bp_value = bp["valueQuantity"]["value"]
bp_unit = bp["valueQuantity"]["unit"]

med_name = med["medicationCodeableConcept"]["coding"][0]["display"]
med_instruction = med["dosageInstruction"][0]["text"]
# ----------------------------------------------------------


def build_prescription_text():
  """Return the prescription text (do not write to disk)."""

  text = f"""
Patient Name  : {patient_name}
Age           : {age}
Gender        : {gender}

---------------------------------------------
Diagnosis:
- {diagnosis}
- Blood Pressure: {bp_value} {bp_unit}

---------------------------------------------
Medication:
- {med_name}
  Instructions: {med_instruction}

---------------------------------------------
Advice:
- Monitor blood pressure regularly
- Stay hydrated
- Avoid sudden standing/sitting
- Follow-up if symptoms persist

---------------------------------------------
Dr. Aditya Garg
Registration No: 123456
Generated on: {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
---------------------------------------------
    """
  return text.strip()


def open_review_window():
  """Open a window to review and edit the generated prescription, then save TXT or export PDF."""
  # Determine initial content source
  filename_base = patient_name
  txt_path = f"{filename_base}.txt"

  # Read existing text (fallback to freshly generated content if not found)
  try:
    with open(txt_path, "r", encoding="utf-8") as f:
      content = f.read()
  except FileNotFoundError:
    # If file not found, generate content in-memory (do NOT write yet)
    content = build_prescription_text()

  # Create review window
  review = tk.Toplevel(root)
  review.title("Review Prescription")
  review.geometry("1920x1080")
  review.grab_set()  # Modal-ish behavior

  # Instructions label
  tk.Label(
    review,
    text="Review or edit the prescription below. Save changes or generate a PDF.",
    font=("Segoe UI", 12),
  ).pack(pady=8)

  # Text area
  text_widget = tk.Text(review, wrap="word", font=("Consolas", 11))
  text_widget.pack(fill="both", expand=True, padx=12, pady=8)
  text_widget.insert("1.0", content)

  # Button bar frame
  btn_frame = tk.Frame(review)
  btn_frame.pack(fill="x", padx=12, pady=8)

  def save_txt():
    edited = text_widget.get("1.0", "end").strip()
    # Let user choose location if desired
    path = filedialog.asksaveasfilename(
      parent=review,
      title="Save Prescription as TXT",
      defaultextension=".txt",
      initialfile=f"{filename_base}.txt",
      filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if not path:
      return
    try:
      with open(path, "w", encoding="utf-8") as f:
        f.write(edited)
      messagebox.showinfo("Saved", f"TXT saved to:\n{path}")
    except Exception as e:
      messagebox.showerror("Error", f"Failed to save TXT:\n{e}")

  def generate_pdf():
    edited = text_widget.get("1.0", "end").strip()

    # Choose PDF file path
    pdf_path = filedialog.asksaveasfilename(
      parent=review,
      title="Save Prescription as PDF",
      defaultextension=".pdf",
      initialfile=f"{filename_base}.pdf",
      filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
    )
    if not pdf_path:
      return

    # Attempt to use reportlab for PDF generation
    try:
      from reportlab.lib.pagesizes import letter
      from reportlab.pdfgen import canvas
      from reportlab.lib.units import inch

      c = canvas.Canvas(pdf_path, pagesize=letter)
      width, height = letter

      # Margin and basic layout
      x_margin = 0.75 * inch
      y_margin = 0.75 * inch
      max_width_chars = 95  # crude wrapping for monospaced feel

      def wrap_lines(text, width_chars):
        lines = []
        for line in text.splitlines():
          if len(line) <= width_chars:
            lines.append(line)
          else:
            # Simple hard wrap
            start = 0
            while start < len(line):
              lines.append(line[start : start + width_chars])
              start += width_chars
        return lines

      lines = wrap_lines(edited, max_width_chars)

      y = height - y_margin
      line_height = 14

      for line in lines:
        if y < y_margin + line_height:
          c.showPage()
          y = height - y_margin
        c.drawString(x_margin, y, line)
        y -= line_height

      c.save()
      messagebox.showinfo("PDF Generated", f"PDF saved to:\n{pdf_path}")
    except ImportError:
      messagebox.showerror(
        "ReportLab not installed",
        "PDF export requires the 'reportlab' package.\n\n"
        "Install it and try again:\n"
        "pip install reportlab",
      )
    except Exception as e:
      messagebox.showerror("Error", f"Failed to generate PDF:\n{e}")

  # Buttons
  save_btn = tk.Button(btn_frame, text="Save TXT", command=save_txt, font=("Segoe UI", 11))
  pdf_btn = tk.Button(btn_frame, text="Generate PDF", command=generate_pdf, font=("Segoe UI", 11))
  close_btn = tk.Button(btn_frame, text="Close", command=review.destroy, font=("Segoe UI", 11))

  save_btn.pack(side="left", padx=4)
  pdf_btn.pack(side="left", padx=4)
  close_btn.pack(side="right", padx=4)



# -------- Windows GUI App --------
ctypes.windll.shcore.SetProcessDpiAwareness(1)

root = tk.Tk()
root.title("Mic Prescription App")
root.geometry("1920x1080")
root.resizable(False, False)

listening = False

# Animation state
mic_animating = False
mic_anim_step = 0
wave_canvas = None

def toggle():
  global listening, mic_animating
  if not listening:
    show_confirmation_window()
  else:
    listening = False
    status_label.config(text="Understood!", fg="#28A745")
    mic_animating = False
    mic_button.config(bg="white")
    root.after(2000, after_understood)  # 2000 ms = 2 seconds
# --- Confirmation Window ---
def show_confirmation_window():
  confirm = tk.Toplevel(root)
  confirm.title("AI Consent & Rights")
  confirm.geometry("1920x1080")
  confirm.grab_set()


  # English and Hindi consent text
  consent_text_en = (
    "I acknowledge that:\n\n"
    "- My voice, text, or medical information may be temporarily processed by AI systems only for the purpose of clinical evaluation.\n"
    "- My personal details will not be shared, sold, or used for commercial purposes.\n"
    "- Only authorized medical staff will have access to the data.\n"
    "- Reasonable safeguards are in place to protect my privacy and confidentiality.\n"
    "- Data will be stored and handled according to hospital/clinic policy and applicable privacy laws.\n\n"
    "I have the right to:\n\n"
    "- Ask questions about how AI is being used.\n"
    "- Decline the use of AI for recording/analysis.\n"
    "- Request deletion of my AI-related data (as per hospital policy).\n"
    "- Opt out at any time without affecting my care.\n"
  )

  consent_text_hi = (
    "मैं स्वीकार करता/करती हूँ कि:\n\n"
    "- मेरी आवाज़, पाठ, या चिकित्सा जानकारी केवल नैदानिक मूल्यांकन के उद्देश्य से अस्थायी रूप से AI सिस्टम द्वारा संसाधित की जा सकती है।\n"
    "- मेरी व्यक्तिगत जानकारी साझा, बेची या व्यावसायिक प्रयोजनों के लिए उपयोग नहीं की जाएगी।\n"
    "- केवल अधिकृत चिकित्सा कर्मचारी ही डेटा तक पहुँच सकते हैं।\n"
    "- मेरी गोपनीयता और सुरक्षा के लिए उचित उपाय किए गए हैं।\n"
    "- डेटा अस्पताल/क्लिनिक नीति और लागू गोपनीयता कानूनों के अनुसार संग्रहीत और संभाला जाएगा।\n\n"
    "मुझे अधिकार है:\n\n"
    "- AI के उपयोग के बारे में प्रश्न पूछने का।\n"
    "- रिकॉर्डिंग/विश्लेषण के लिए AI के उपयोग से इनकार करने का।\n"
    "- अपनी AI-संबंधित डेटा को हटाने का अनुरोध करने का (अस्पताल नीति के अनुसार)।\n"
    "- किसी भी समय बाहर निकलने का, बिना देखभाल पर प्रभाव डाले।\n"
  )

  # Language state
  lang = {"current": "en"}

  # Button text for both languages
  btn_texts = {
    "en": {"accept": "Accept & Continue", "decline": "Decline"},
    "hi": {"accept": "स्वीकारें और आगे बढ़ें", "decline": "अस्वीकार करें"}
  }

  # title label (will be updated to selected language)
  title_label = tk.Label(confirm, text="Consent & Rights", font=("Segoe UI", 16, "bold"), pady=10)
  title_label.pack()

  def update_text():
    text_widget.config(state="normal")
    text_widget.delete("1.0", "end")
    if lang["current"] == "en":
      text_widget.insert("1.0", consent_text_en)
    else:
      text_widget.insert("1.0", consent_text_hi)
    text_widget.config(state="disabled")
    # Update button text
    accept_btn.config(text=btn_texts[lang["current"]]["accept"])
    decline_btn.config(text=btn_texts[lang["current"]]["decline"])
    # Update header/title according to selected language
    if lang["current"] == "en":
      title_label.config(text="Consent & Rights")
    else:
      title_label.config(text="सहमति और अधिकार")

  text_widget = tk.Text(confirm, wrap="word", font=("Segoe UI", 12), height=20, width=70)
  # Put the large editable text area above, and controls in a fixed bottom bar
  text_widget.pack(fill="both", expand=True, padx=16, pady=8)

  # Bottom bar frame to ensure controls are always visible
  bottom_bar = tk.Frame(confirm)
  bottom_bar.pack(side="bottom", fill="x", padx=16, pady=8)

  # Language dropdown (left side of bottom bar)
  lang_options = ["English", "हिन्दी"]
  lang_map = {"English": "en", "हिन्दी": "hi"}
  lang_var = tk.StringVar(value=lang_options[0])

  def on_lang_select(event=None):
    lang["current"] = lang_map[lang_var.get()]
    update_text()

  lang_dropdown = tk.OptionMenu(bottom_bar, lang_var, *lang_options, command=lambda _: on_lang_select())
  lang_dropdown.config(font=("Segoe UI", 11), bg="#F7CA18", fg="black", width=14)
  lang_dropdown.pack(side="left", padx=(0, 12))

  # Button frame (right side of bottom bar)
  btn_frame = tk.Frame(bottom_bar)
  btn_frame.pack(side="right")

  def accept():
    global listening, mic_animating
    listening = True
    status_label.config(text="Listening...", fg="#0078D4")
    mic_animating = True
    animate_mic()
    confirm.destroy()

  def decline():
    confirm.destroy()

  accept_btn = tk.Button(btn_frame, text=btn_texts[lang["current"]]["accept"], command=accept, font=("Segoe UI", 12), bg="#28A745", fg="white", width=18)
  decline_btn = tk.Button(btn_frame, text=btn_texts[lang["current"]]["decline"], command=decline, font=("Segoe UI", 12), bg="#DC3545", fg="white", width=10)
  accept_btn.pack(side="left", padx=8)
  decline_btn.pack(side="right", padx=8)

  # Now update text and button labels after packing
  update_text()

def after_understood():
  status_label.config(text="Please review the generated prescription.", fg="#28A745")
  open_review_window()

# --- Mic Waveform Animation ---
import math
def animate_mic():
  """Draw a simple animated waveform on `wave_canvas` while `mic_animating` is True.

  This replaces the previous color-pulse animation with a bar-waveform visualization.
  """
  global mic_anim_step
  if not mic_animating:
    mic_button.config(bg="white")
    try:
      wave_canvas.delete("all")
    except Exception:
      pass
    return

  # Canvas dimensions
  try:
    w = wave_canvas.winfo_width()
    h = wave_canvas.winfo_height()
  except Exception:
    w, h = 300, 60

  wave_canvas.delete("all")

  bars = 22
  bar_w = max(2, int(w / (bars * 1.8)))
  spacing = max(2, int((w - bars * bar_w) / (bars + 1)))

  mic_anim_step = (mic_anim_step + 1) % 100000

  for i in range(bars):
    # each bar has a phase offset so the waveform moves
    phase = mic_anim_step * 0.12 + i * 0.45
    amp = (math.sin(phase) + 1) / 2  # 0..1
    # Vary amplitude slightly per bar for a natural look
    height = amp * h * (0.25 + 0.75 * abs(math.sin(mic_anim_step * 0.02 + i)))
    x = spacing + i * (bar_w + spacing)
    y1 = (h - height) / 2
    y2 = y1 + height
    # color using a fixed accent color
    color = "#2196F3"
    wave_canvas.create_rectangle(x, y1, x + bar_w, y2, fill=color, outline=color)

  root.after(30, animate_mic)


mic_frame = tk.Frame(root)
mic_frame.place(relx=0.5, rely=0.5, anchor="center")

mic_button = tk.Button(
  mic_frame,
  text="🎤",
  font=("Segoe UI Emoji", 55),
  command=toggle,
  relief="flat",
  bg="white",
  activebackground="white",
)
# Pack mic button above the waveform canvas so waveform appears below mic
mic_button.pack(pady=6)

# Waveform canvas (created once, used by animate_mic) - placed below mic and centered
wave_canvas = tk.Canvas(mic_frame, width=360, height=72, highlightthickness=0)
wave_canvas.pack(pady=(8, 0))

status_label = tk.Label(
  mic_frame,
  text="Click the mic",
  font=("Segoe UI", 20),
)
status_label.pack(pady=10)

root.mainloop()
