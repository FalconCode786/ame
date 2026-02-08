# Al Muslim Engineers - Solar Solutions Web Application

## Overview
A comprehensive Flask-based ecommerce platform for solar products and services, serving Rawalpindi, Pakistan. Features include product catalog, solar calculator, net/gross metering applications, maintenance requests, shopping cart, and admin dashboard.

## Project Architecture
- **Framework**: Flask 3.0.0 (Python)
- **Database**: SQLite (via Flask-SQLAlchemy)
- **Template Engine**: Jinja2
- **Frontend**: Server-rendered HTML with CSS/JS (no build step)
- **File Structure**:
  - `app.py` - Main application (routes, models, logic)
  - `templates/` - Jinja2 HTML templates
  - `static/css/` - Stylesheets (style.css, premium.css)
  - `static/js/` - JavaScript (main.js, turbo.js)
  - `static/images/` - Product and project images
  - `instance/solar_app.db` - SQLite database file

## Key Features
- User authentication (signup/login)
- Product catalog with shopping cart and checkout
- Solar calculator (AI-based recommendations)
- Net/Gross metering applications
- Simple solar setup applications
- Maintenance request system
- Customer feedback
- Project gallery
- Admin dashboard (products, orders, applications, maintenance, gallery management)

## Running
- **Development**: `python app.py` (runs on 0.0.0.0:5000)
- **Production**: `gunicorn --bind=0.0.0.0:5000 --reuse-port app:app`

## Recent Changes
- 2026-02-08: Initial Replit setup - installed Python 3.11, Flask dependencies, configured workflow and deployment
