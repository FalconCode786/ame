# Al Muslim Engineers - Solar Solutions

A comprehensive Flask-based ecommerce web application for Al Muslim Engineers, a solar solutions agency serving Rawalpindi, Pakistan.

## Features

### Client Features
- **User Authentication**: Secure login and registration system
- **AI Solar Calculator**: Get personalized solar system recommendations based on electricity bill and roof area
- **Net Metering Applications**: Apply for net metering (5kW and above)
- **Gross Metering Applications**: Apply for gross metering (1kW to 50kW)
- **Real-time Application Tracking**: Track application status with reference numbers
- **E-commerce**: Browse and purchase solar products (panels, inverters, batteries, etc.)
- **Shopping Cart**: Add products, update quantities, checkout
- **Maintenance Requests**: Request cleaning, repair, inspection, or upgrade services
- **Feedback System**: Submit ratings and reviews
- **Project Gallery**: View completed solar installations

### Admin Features
- **Dashboard**: Overview with statistics and recent activities
- **Product Management**: CRUD operations for solar products
- **Application Management**: Review and update metering applications
- **Order Management**: Process and track customer orders
- **Maintenance Management**: Handle maintenance requests
- **Gallery Management**: Add/edit/delete project showcases
- **Feedback Management**: Approve customer reviews

### Technical Features
- **Dark/Light Mode**: Toggle between themes
- **Responsive Design**: Works on all devices
- **AI Recommendations**: Smart solar system sizing
- **Real-time Status Updates**: Track applications in real-time
- **Secure Authentication**: Password hashing and session management

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (SQLAlchemy ORM)
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with CSS Variables
- **Icons**: Font Awesome
- **Fonts**: Google Fonts (Playfair Display, Inter, Source Sans Pro)

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd solar_app
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

6. Run the application:
```bash
python app.py
```

7. Access the application at `http://localhost:5000`

## Default Credentials

### Admin
- Email: admin@almuslim.com
- Password: admin123

## Folder Structure

```
solar_app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel deployment config
├── .env.example          # Environment variables template
├── README.md             # This file
├── instance/             # Database directory
│   └── solar_app.db      # SQLite database
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── js/
│   │   └── main.js       # Main JavaScript
│   └── images/           # Images and uploads
│       ├── logo.png
│       ├── hero-bg.jpg
│       ├── solar-panel-1.jpg
│       ├── inverter-1.jpg
│       ├── battery-1.jpg
│       ├── controller-1.jpg
│       ├── mounting-1.jpg
│       ├── cables-1.jpg
│       ├── project-1.jpg
│       ├── project-2.jpg
│       ├── project-3.jpg
│       └── uploads/      # User uploaded files
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── index.html        # Landing page
    ├── login.html        # Login page
    ├── signup.html       # Registration page
    ├── client_dashboard.html
    ├── apply_metering.html
    ├── application_status.html
    ├── products.html
    ├── product_detail.html
    ├── cart.html
    ├── checkout.html
    ├── order_confirmation.html
    ├── maintenance.html
    ├── feedback.html
    ├── gallery.html
    ├── project_detail.html
    ├── solar_calculator.html
    ├── admin_dashboard.html
    ├── admin_products.html
    ├── admin_add_product.html
    ├── admin_edit_product.html
    ├── admin_applications.html
    ├── admin_application_detail.html
    ├── admin_orders.html
    ├── admin_order_detail.html
    ├── admin_maintenance.html
    ├── admin_maintenance_detail.html
    ├── admin_gallery.html
    ├── admin_add_gallery.html
    ├── admin_edit_gallery.html
    ├── admin_feedback.html
    ├── 404.html
    └── 500.html
```

## Deployment

### Vercel Deployment

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

### Manual Deployment

1. Set environment variables:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
```

2. Run with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## API Endpoints

### Public Endpoints
- `GET /` - Home page
- `GET /products` - Product catalog
- `GET /product/<id>` - Product detail
- `GET /gallery` - Project gallery
- `GET /solar-calculator` - AI Solar Calculator
- `GET /api/application-status/<ref>` - Check application status

### Authentication Required
- `GET/POST /login` - Login
- `GET/POST /signup` - Register
- `GET /logout` - Logout
- `GET /dashboard` - Client dashboard
- `GET/POST /apply-metering` - Apply for metering
- `GET /application-status/<id>` - View application status
- `GET/POST /cart` - Shopping cart
- `GET/POST /checkout` - Checkout
- `GET/POST /maintenance` - Maintenance request
- `GET/POST /feedback` - Submit feedback

### Admin Only
- `GET /admin` - Admin dashboard
- `GET/POST /admin/products` - Manage products
- `GET/POST /admin/product/add` - Add product
- `GET/POST /admin/product/edit/<id>` - Edit product
- `GET /admin/product/delete/<id>` - Delete product
- `GET /admin/applications` - View applications
- `GET/POST /admin/application/<id>` - Application detail
- `GET /admin/orders` - View orders
- `GET/POST /admin/order/<id>` - Order detail
- `GET /admin/maintenance` - View maintenance requests
- `GET/POST /admin/maintenance/<id>` - Maintenance detail
- `GET /admin/gallery` - Manage gallery
- `GET/POST /admin/gallery/add` - Add gallery project
- `GET/POST /admin/gallery/edit/<id>` - Edit gallery project
- `GET /admin/gallery/delete/<id>` - Delete gallery project
- `GET /admin/feedback` - Manage feedback

## AI Solar Calculator Algorithm

The AI calculator uses the following parameters:
- **Peak Sun Hours**: 5.5 hours (Rawalpindi average)
- **System Loss Factor**: 80%
- **Electricity Rate**: PKR 25/unit (approximate)
- **Cost per kW**: PKR 80,000 (installed)

Formula:
```
Daily Units = Monthly Bill / Rate / 30
Required Capacity = Daily Units / (Peak Sun Hours * Loss Factor)
Monthly Generation = Capacity * Peak Sun Hours * 30 * Loss Factor
Monthly Savings = Monthly Generation * Rate
Payback Period = Total Cost / Annual Savings
```

## Net Metering Eligibility

- **Net Metering**: Available for systems 5kW and above
- **Gross Metering**: Available for systems 1kW to 50kW
- **Service Area**: Rawalpindi only

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## License

This project is proprietary and confidential. All rights reserved by Al Muslim Engineers.

## Support

For support, contact:
- Email: info@almuslimengineers.com
- Phone: +92-300-1234567
- Address: Main Office, Saddar, Rawalpindi, Pakistan

---

**Al Muslim Engineers** - Powering Pakistan with Clean Energy
