// Copyright (c) 2025, Amey Golait and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Prescription", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Prescription", {
    refresh(frm) {
        frm.add_custom_button("Send WhatsApp", function () {
            frappe.call({
                method: "clinic_app.api.send_prescription_whatsapp",
                args: {
                    prescription_name: frm.doc.name
                },
                callback: function (r) {
                    if (!r.exc) {
                        frappe.msgprint(r.message);
                    }
                }
            });
        });
    }
});

