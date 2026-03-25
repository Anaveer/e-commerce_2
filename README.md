# 🛒 ShopAWS — E-Commerce App

A full-stack Django + PostgreSQL e-commerce application built as part of the **AWS Internship Training Program**, deployed on Amazon EC2.

---

## 🚀 Tech Stack

| Layer      | Technology              |
|------------|-------------------------|
| Backend    | Python 3.11 + Django 4.2 |
| Database   | PostgreSQL 15           |
| Web Server | Gunicorn + Nginx        |
| Hosting    | AWS EC2 (Amazon Linux)  |
| Storage    | WhiteNoise (static)     |

---

## ✅ Features

- **Product CRUD** — Create, Read, Update, Delete products (admin only)
- **Category Management** — Organize products by category
- **Shopping Cart** — Session-based cart with quantity update/remove
- **User Auth** — Register, Login, Logout
- **Checkout & Orders** — Place orders with shipping details
- **Order Tracking** — Customers view their own orders
- **Admin Order Management** — Staff can update order status
- **Search & Filter** — Search products by name, filter by category
- **Django Admin Panel** — Full database management at `/admin`

---

## 📁 Project Structure

```
aws-ecommerce/
├── ecommerce/           # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/               # Main app
│   ├── models.py        # Product, Category, Order, OrderItem
│   ├── views.py         # All views (CRUD, cart, auth)
│   ├── urls.py          # URL routing
│   ├── forms.py         # Django forms
│   ├── admin.py         # Admin registration
│   ├── context_processors.py
│   └── templates/store/ # HTML templates
├── requirements.txt
├── manage.py
├── deploy.sh            # EC2 auto-deploy script
└── .env.example
```

---

## 🏃 Local Setup

```bash
# 1. Clone repo
git clone https://github.com/YOUR_USERNAME/aws-ecommerce.git
cd aws-ecommerce

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 5. Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE ecommerce_db;"

# 6. Run migrations
python manage.py migrate

# 7. Create superuser
python manage.py createsuperuser

# 8. Run server
python manage.py runserver
# Visit: http://localhost:8000
```

---

## ☁️ AWS EC2 Deployment

### Step 1 — Launch EC2
- AMI: **Amazon Linux 2023**
- Type: **t2.micro** (free tier)
- Security Group Inbound Rules:
  - SSH → Port 22 → My IP
  - HTTP → Port 80 → 0.0.0.0/0

### Step 2 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/aws-ecommerce.git
git push -u origin main
```

### Step 3 — Connect to EC2 & Deploy
```bash
# Connect
chmod 400 your-key.pem
ssh -i your-key.pem ec2-user@YOUR_EC2_IP

# Run deploy script
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/aws-ecommerce/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### Step 4 — Access the App
- **Website:** `http://YOUR_EC2_IP`
- **Admin Panel:** `http://YOUR_EC2_IP/admin`
- Default admin: `admin` / `Admin@1234` *(change after login!)*

---

## 🔑 Default Admin Credentials

After running deploy.sh:
- Username: `admin`
- Password: `Admin@1234`
- **Change immediately after first login!**

---

## 📊 Database Models

```
Category     → name, slug, description
Product      → name, slug, category, description, price, stock, image, is_active
Order        → user, status, total_price, full_name, email, address, city
OrderItem    → order, product, quantity, price
```

---

*Built for AWS Internship Training Program — Deployed on Amazon EC2*
