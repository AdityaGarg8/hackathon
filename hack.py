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
Patient Name : {patient_name}
Age          : {age}
Gender       : {gender}

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

def toggle():
    global listening
    listening = not listening

    if listening:
        status_label.config(text="Listening...", fg="#0078D4")
    else:
        status_label.config(text="Understood!", fg="#28A745")
        root.after(2000, after_understood)  # 2000 ms = 2 seconds

def after_understood():
  # Prepare review without auto-creating the TXT
  status_label.config(text="Please review the generated prescription.", fg="#28A745")
  open_review_window()


mic_button = tk.Button(
    root,
    text="🎤",
    font=("Segoe UI Emoji", 55),
    command=toggle,
    relief="flat",
    bg="white",
    activebackground="white",
)
mic_button.pack(pady=20)

status_label = tk.Label(
    root,
    text="Click the mic",
    font=("Segoe UI", 20),
)
status_label.pack(pady=10)

root.mainloop()
