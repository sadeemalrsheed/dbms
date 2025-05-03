using System;
using System.Windows.Forms;

namespace ECommerceWinFormsFull {
    public class MainForm : Form {
        public MainForm() {
            Text = "E-Commerce Management System";
            Width = 600;
            Height = 400;

            Label titleLabel = new Label() {
                Text = "Welcome to Online Store",
                AutoSize = true,
                Font = new System.Drawing.Font("Arial", 18),
                Location = new System.Drawing.Point(180, 30)
            };
            Controls.Add(titleLabel);

            Button productBtn = new Button() {
                Text = "View Products",
                Location = new System.Drawing.Point(230, 100),
                Width = 120
            };
            productBtn.Click += (s, e) => {
                ProductForm pf = new ProductForm();
                pf.Show();
            };
            Controls.Add(productBtn);
        }
    }
}
