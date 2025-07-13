# CURE CONNECT

CURE CONNECT is an AI-powered Virtual Receptionist Hub that streamlines front-desk operations in healthcare facilities. By automating appointment scheduling, routine queries, and patient–doctor communications, the system addresses challenges such as long wait times, missed appointments, and inefficient administrative processes, ultimately enhancing patient engagement and operational efficiency.

## Introduction

CURE CONNECT is designed to overcome the limitations of manual and basic automated appointment systems. It leverages advanced natural language processing (NLP) models to power chatbots, enabling both text and voice interactions. This not only simplifies appointment management but also facilitates real-time, post-appointment communication between patients and healthcare providers.

## Features

- **Automated Appointment Management**  
  Schedule, reschedule, and cancel appointments using AI-powered agents without manual intervention.
  
- **AI-Driven Patient-Doctor Communication**  
  Seamless real-time chat enables post-appointment follow-ups and immediate responses to routine queries.
  
- **Routine Query Handling**  
  An intelligent AI agent manages common inquiries (e.g., prescription refills, general information) and escalates complex issues when necessary.
  
- **Integration with Hospital Systems**  
  Real-time updates and integration with hospital databases ensure accurate appointment and patient record management.
  
- **Personalized Patient Engagement**  
  The AI learns patient preferences over time, delivering tailored notifications and follow-up care.
  
- **Data Privacy and Security**  
  Implements robust security protocols including SSL/TLS encryption, OAuth 2.0, and JWT-based user authentication.

## Technology Stack

- **Frontend:**  
  HTML, CSS, JavaScript – for building responsive patient and receptionist web interfaces.
  
- **Backend:**  
  Flask (Python) – a lightweight framework managing HTTP requests, routing, and business logic.
  
- **Database:**  
  SQLite – a lightweight, serverless relational database for storing patient and appointment data.
  
- **AI Models:**  
  PyTorch – used for natural language processing (NLP) to power chatbot intelligence.
  
- **Communication Services:**  
  Twilio – for managing SMS and email notifications regarding appointments and follow-ups.
  
- **Security:**  
  OAuth 2.0 and JSON Web Tokens (JWT) – ensure secure user authentication and data access.
  
- **Real-Time Communication:**  
  WebSockets or Firebase – enable instant messaging between patients and healthcare providers.

## Architecture

CURE CONNECT follows a layered architecture to ensure scalability, security, and ease of maintenance:

1. **User Interface Layer:**  
   - **Patient Portal:** For scheduling appointments, viewing notifications, and interacting with the AI chatbot.  
   - **Receptionist Dashboard:** For monitoring appointments, managing escalated queries, and overseeing system notifications.
  
2. **Application Logic Layer:**  
   - Flask-based backend handling API requests related to appointment management, user sessions, and chat interactions.
  
3. **Agentic AI Layer:**  
   - PyTorch-based NLP models integrated with the Gemini API to process and triage user queries.
  
4. **Database Layer:**  
   - SQLite stores patient records, appointment data, and chatbot logs.
  
5. **Integration Layer:**  
   - Third-party APIs such as Twilio for notifications and additional hospital system integrations.
  
6. **Security & Communication Layers:**  
   - SSL/TLS encryption ensures secure data transmission along with real-time updates via WebSockets or Firebase.  
> *(For a detailed view, refer to the project documentation(ProjectReport).)*

## Results

- **Increased Efficiency:** Automated workflows have significantly reduced administrative workload and minimized patient wait times.
- **Enhanced Communication:** Real-time AI-driven chat enables continuous interactions between patients and doctors, even for post-appointment follow-ups.
- **User-Friendly Interfaces:** Both patients and healthcare staff benefit from intuitive dashboards that simplify management and interaction.
- **Integration Success:** Seamless integration with hospital systems ensures that patient records and appointment data remain accurate and up-to-date.

## Future Scope

- **AI-Based Disease Detection:** Integrate image analysis (using CNNs or Transformers) for early diagnostic support.
- **Voice-Activated Operations:** Expand query handling and appointment management with voice recognition technology for enhanced accessibility.
- **Telemedicine Capabilities:** Incorporate video consultations and real-time health monitoring to serve remote or underserved populations.
- **Patient Sentiment Analysis:** Utilize sentiment analysis to automatically identify and address patient concerns based on communication feedback.
- **Personalized Healthcare Recommendations:** Leverage patient data to provide custom health tips, appointment reminders, and wellness advice.
- **EHR Integration:** Enhance decision-making by integrating with Electronic Health Records (EHR) for a comprehensive view of patient history.

## Getting Started

To set up and run CURE CONNECT locally:

1. **Clone the Repository:**  
