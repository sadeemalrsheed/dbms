using System;
using System.Windows.Forms;

namespace ECommerceWinFormsFull {
    public class ProductForm : Form {
        public ProductForm() {
            Text = "Product List";
            Width = 500;
            Height = 300;

            ListBox productList = new ListBox() {
                Dock = DockStyle.Fill
            };

            // Sample static data, you can replace with DB values later
            productList.Items.Add("1. Clean Code - 120.50 SAR");
            productList.Items.Add("2. AI: A Modern Approach - 220.00 SAR");
            productList.Items.Add("3. Samsung Galaxy S21 - 3100.00 SAR");
            productList.Items.Add("4. Apple AirPods Pro - 999.99 SAR");
            productList.Items.Add("5. Nike Running Shoes - 350.00 SAR");
            productList.Items.Add("6. Adidas Hoodie - 200.00 SAR");

            Controls.Add(productList);
        }
    }
}
