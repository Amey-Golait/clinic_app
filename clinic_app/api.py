import frappe
import requests

@frappe.whitelist()
def send_prescription_whatsapp(prescription_name):
    prescription = frappe.get_doc("Prescription", prescription_name)

    if not prescription.appointment:
        frappe.throw("Appointment must be linked to Prescription.")

    appointment = frappe.get_doc("Clinic Appointment", prescription.appointment)
    patient = frappe.get_doc("Patient", appointment.patient)

    phone_number = patient.phone
    if not phone_number:
        frappe.throw("Patient does not have a phone number.")

    # Simulate WhatsApp message
    webhook_url = "https://webhook.site/e974659b-5135-49e9-8dec-8dc8b40c7c21"
    message = f"Hello {patient.patient_name}, your prescription ({prescription.name}) is ready."

    data = {
        "to": phone_number,
        "message": message,
        "prescription_link": frappe.utils.get_url_to_form("Prescription", prescription.name)
    }

    try:
        res = requests.post(webhook_url, json=data)
        res.raise_for_status()
        return f"Message sent to WhatsApp (simulated) for {patient.patient_name} at {phone_number}"
    except Exception as e:
        frappe.throw(f"Error sending message: {str(e)}")
