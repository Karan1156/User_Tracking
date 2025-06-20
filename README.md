# 🛰️ User Tracking & Blog Dashboard

A Django-based full-stack web application where users can create accounts, post blogs, and track visitors via custom-generated links. Admins have special privileges to manage user accounts.

> **Live Demo**: [Click to Visit](https://user-tracking-svrv.onrender.com/)

---

## 🔍 Features

### 👤 User Dashboard
- Users can register, log in, and access a personal dashboard
- Generate a tracking link to share with others
- When someone clicks the link and submits their name, the original user receives:
  - The visitor's **name**
  - The **location** (approximate) of the visitor

### 🛡️ Admin Dashboard
- Admins can:
  - View all users
  - Delete any user
  - View all submitted data

### 📝 Blog Integration
- Users can create and view blog posts
- Blogs are linked to users and visible on the dashboard

---

## ⚙️ Tech Stack

| Layer        | Technology            |
|--------------|------------------------|
| Backend      | Django                 |
| Frontend     | HTML, CSS, JavaScript  |
| Database     | SQLite (default Django DB) |
| Deployment   | Render.com             |
| Extras       | IP/location tracking via external services |

---

## 🚀 Installation (Local Setup)

### 1. Clone the repository:
```bash
git clone https://github.com/your-username/user-tracking-django.git
cd user-tracking-django
