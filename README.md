# 🪞 Darpan — AI-Powered Civic Issue Reporting & Tracking Platform

<div align="center">

### A smarter way for citizens to report, track, and understand civic issues.

Report an issue. Let AI analyze it. Track its progress. Build a better community.

<br/>

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-000000?style=for-the-badge&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite)
![AI](https://img.shields.io/badge/AI-CLIP%20Powered-7C3AED?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)

</div>

---

## 🌍 The Problem

Civic issues such as potholes, garbage accumulation, damaged streetlights, and public infrastructure problems often suffer from:

- ❌ Difficult and fragmented reporting processes
- ❌ Lack of visibility after reporting
- ❌ Duplicate complaints for the same issue
- ❌ Limited transparency in issue resolution
- ❌ No intelligent analysis of recurring civic problems

**Darpan** aims to create a transparent digital layer between citizens and civic issue management.

---

# ✨ What is Darpan?

**Darpan** is an AI-powered civic issue reporting and tracking platform where users can report problems in their community using an image and location.

The platform analyzes submitted issue images using AI, helps categorize civic problems, detects potential duplicate reports, and provides users with a centralized dashboard to track reported issues.

The goal is simple:

> **Make civic problems visible, trackable, and easier to act upon.**

---

# 🚀 Key Features

## 🤖 AI-Powered Issue Analysis

Darpan uses an AI image classification pipeline to analyze uploaded images and identify the type of civic issue.

Examples include:

- 🕳️ Potholes
- 🗑️ Garbage
- 💡 Streetlight issues
- 🛣️ Infrastructure problems

The AI model helps reduce manual categorization and improves the reporting workflow.

---

## 📸 Image-Based Issue Reporting

Users can submit civic issues with:

- Issue image
- Description
- Category
- Location information

This provides visual context and makes reports easier to understand.

---

## 🗺️ Interactive Issue Map

Reported issues can be visualized geographically, allowing users to explore problems across different locations.

This creates a more intuitive way to understand:

- Where issues are concentrated
- Which locations have multiple reports
- The distribution of civic problems

---

## 🔍 Duplicate Issue Detection

Before creating a new report, Darpan can identify potentially similar existing issues.

This helps reduce:

- Duplicate complaints
- Repeated reporting
- Fragmented issue tracking

Instead of creating multiple reports for the same problem, users can interact with existing reports.

---

## 📊 Personalized Citizen Dashboard

Users get a centralized dashboard to monitor their civic reports.

The dashboard provides visibility into:

- Total reported issues
- Current issue status
- Issue categories
- Report history
- Images and locations
- Resolution progress

---

## 📈 AI-Assisted Insights

The platform is designed to analyze issue and transaction-style data patterns to provide intelligent insights.

Potential insights include:

- Frequently occurring issue categories
- Areas with repeated problems
- Issue trends
- Reporting patterns

---

## 🔐 Simple User Authentication

Users can:

- Register using a mobile number
- Login using their registered mobile number
- Maintain a session during platform usage
- Logout securely

The authentication flow is intentionally lightweight for the current version of the project.

---

# 🧠 How the System Works

```text
┌───────────────┐
│    Citizen    │
└───────┬───────┘
        │
        ▼
┌──────────────────────┐
│   Report an Issue    │
│                      │
│ 📸 Upload Image      │
│ 📍 Add Location      │
│ 📝 Add Description   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│     AI Pipeline      │
│                      │
│  Image Classification│
│  Issue Categorization│
│  Similarity Analysis │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Issue Database     │
│                      │
│  SQLite Storage      │
│  Images + Metadata   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Citizen Dashboard &  │
│ Interactive Map      │
└──────────────────────┘

Architecture

                 ┌──────────────────┐
                 │      User        │
                 │   Web Browser    │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   Flask Server   │
                 │    app.py        │
                 └───────┬──────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
   ┌────────────┐  ┌────────────┐  ┌──────────────┐
   │ AI / CLIP  │  │  SQLite DB │  │ Static Files │
   │ Analysis   │  │            │  │ Images       │
   └────────────┘  └────────────┘  └──────────────┘

Tech Stack

| Technology       | Purpose                                     |
| ---------------- | ------------------------------------------- |
| **Python**       | Core programming language                   |
| **Flask**        | Backend web framework                       |
| **SQLite**       | Database management                         |
| **HTML5**        | Page structure                              |
| **CSS3**         | UI and responsive design                    |
| **JavaScript**   | Interactive frontend features               |
| **Bootstrap**    | Responsive UI components                    |
| **CLIP**         | AI-powered image understanding              |
| **Transformers** | Machine learning model integration          |
| **Pillow**       | Image processing                            |
| **Docker**       | Containerization and deployment consistency |

📂 Project Structure
DARPAN/
│
├── app.py
├── requirements.txt
├── Dockerfile
├── README.md
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── report_issue.html
│   ├── issue_detail.html
│   └── ...
│
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
│
└── instance/
    └── database.db

⚙️ Getting Started
1️⃣ Clone the Repository
git clone https://github.com/YOUR_USERNAME/Darpan-Issue-Tracker.git
cd Darpan-Issue-Tracker
2️⃣ Create a Virtual Environment
Windows
python -m venv myapp
myapp\Scripts\activate
macOS / Linux
python3 -m venv myapp
source myapp/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Run the Application
flask run

Open:

http://127.0.0.1:5000
🐳 Run with Docker

Build the image:

docker build -t darpan .

Run the container:

docker run -p 5000:5000 darpan

Then open:

http://localhost:5000

🧩 Engineering Highlights

This project was built with a focus on more than just UI development.

Separation of Responsibilities

The application separates:

Frontend templates
Backend routes
Database operations
AI image processing
Static file management
Real Data Flow

The application works with actual stored issue data rather than static mock data.

User Input
    ↓
Backend Validation
    ↓
Database Storage
    ↓
AI Processing
    ↓
Dashboard / Map Visualization
Modular AI Integration

The AI component is integrated into the application workflow, allowing image understanding to become part of the issue reporting process.

The architecture can be extended to support:

Better image classification models
Issue severity prediction
Automatic prioritization
Similarity search
Smart recommendations
🔮 Future Improvements

Some potential next steps for Darpan include:

 Government/authority dashboard
 Role-based access control
 Issue priority prediction
 Automated authority assignment
 Email or SMS notifications
 Real-time issue updates
 Public issue voting
 Advanced duplicate detection
 Analytics dashboard
 PostgreSQL migration
 Cloud deployment
 CI/CD pipeline
🎯 Why This Project?

Darpan was built to explore how modern web development and AI can work together to solve a practical problem.

Instead of building an isolated AI model or a basic CRUD application, this project focuses on integrating:

AI + Full Stack Development + Database Design + Image Processing + Deployment

into a single end-to-end application.

The project demonstrates practical experience with:

Building backend APIs and routes
Database integration
Session-based authentication
File uploads and image handling
AI/ML model integration
Responsive frontend development
Docker containerization
End-to-end application architecture
