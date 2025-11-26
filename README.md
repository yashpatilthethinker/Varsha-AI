🤖 Varsha AI – Intelligent Document & Chat Assistant

Varsha AI is a smart, Streamlit-based AI assistant powered by Google Gemini. It supports natural chat, document understanding, summarization, sentiment analysis, keyword extraction, and exporting chats in PDF or text format—all within a clean and modern UI.


🚀 Features

AI Chat: Friendly conversational assistant using Gemini models
Document Intelligence: Upload and analyze PDF, DOCX, PPTX, and TXT files
Smart Tools:

  Summarization
  Sentiment analysis
  Keyword & entity extraction
  Document-based Q&A
  Chat Export: Save chat history as PDF or TXT
  Modern UI: Streamlit design with gradient header, suggestion prompts, and collapsible sections


🗂️ Tech Stack

Streamlit – UI framework
Google Generative AI (Gemini) – AI model
PyMuPDF / python-docx / python-pptx – Document processing
ReportLab – PDF export
dotenv – Environment variable management


🔧 Setup & Installation

1️⃣ Clone the Repo

git clone https://github.com/yashpatilthethinker/Varsha-AI.git
cd varsha-ai


2️⃣ Install Dependencies

pip install -r requirements.txt


3️⃣ Add Your API Key

Create a `.env` file:
GEMINI_API_KEY=your_api_key_here
APP_NAME=Varsha AI
DEBUG_MODE=False


4️⃣ Run the App

streamlit run streamlit_app.py.py


📌 Project Structure


Varsha-AI/
│── app.py                 # Main Streamlit UI
│── gemini_integration.py  # GeminiChat class
│── document_processor.py  # Document extraction logic
│── requirements.txt       # Requirements
│── .env.example
│── .gitignore
└── assets/                



👤 Author

Yash Patil
📧 Email: [yashpatil7157@gmail.com]




🙌 Contributing

Contributions and feature suggestions are welcome.
Feel free to open an issue or submit a pull request.


⭐ Support

If you like this project, please give it a ⭐ on GitHub!


