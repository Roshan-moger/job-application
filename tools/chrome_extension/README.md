# 🚀 AI Job Auto-Apply & Form Auto-Filler (Chrome Extension)

A high-performance Chrome Extension (Manifest V3) designed to **1-click auto-fill job applications** across **LinkedIn Easy Apply, Naukri, Indeed, Greenhouse, Lever, Workday**, and company career pages.

Tailored and grounded directly in **Roshan Moger's verified profile** (2.5+ Years Full Stack Experience, ASP.NET Core, React.js, MCP, and Generative AI).

---

## ✨ Features

- **⚡ 1-Click Form Auto-Filler:** Intelligently detects and fills:
  - First Name, Last Name, Full Name
  - Email, Phone Number, City, State, Country
  - Current Title (*Associate Software Engineer*) & Current Employer (*ExcelSoft Technologies*)
  - Total Experience (*2.5 Years*) & Relevant Experience
  - Notice Period (*15 to 30 Days*)
  - Current CTC & Expected CTC
  - Portfolio Website ([`roshan-devhub.netlify.app`](https://roshan-devhub.netlify.app))
  - LinkedIn Profile & GitHub Repository URLs
- **🤖 In-Page Floating HUD:** A sleek, non-intrusive floating button appears directly on the bottom-right corner of every job application page (`🤖 AI Auto-Fill`). You don't even have to open the extension popup!
- **📝 Instant AI Cover Letter / Pitch:** One click inserts a tailored elevator pitch highlighting your .NET Core, React, and Model Context Protocol (MCP) / Gemini AI achievements.
- **🛡️ Native Framework Event Dispatch:** Simulates real user input (`input`, `change`, `blur`), guaranteeing that modern single-page applications (React, Angular, Vue, Workday) register the filled state without form validation errors.
- **👁️ Visual Verification:** Auto-filled fields are highlighted in a subtle glowing emerald green so you can review everything before clicking Submit.
- **📋 1-Click Clipboard Hub:** Quick-copy buttons for Phone, Email, Portfolio, and LinkedIn.

---

## 🛠️ Step-by-Step Installation (Takes 30 Seconds)

### Step 1: Open Chrome Extensions
1. Open **Google Chrome** (or Microsoft Edge / Brave).
2. Type `chrome://extensions/` into the URL bar and press **Enter**.

### Step 2: Enable Developer Mode
1. In the top-right corner of the Extensions page, toggle the **"Developer mode"** switch to **ON**.

### Step 3: Load the Extension
1. Click the **"Load unpacked"** button in the top-left corner.
2. Navigate to your workspace folder and select the `tools/chrome_extension` directory:
   ```
   c:\Users\DELL\Desktop\30Days-leraning\ai-job-search\tools\chrome_extension
   ```
3. Click **Select Folder**.

### Step 4: Pin the Extension
1. Click the puzzle-piece icon (**Extensions**) in Chrome’s toolbar.
2. Click the pin icon next to **"AI Job Auto-Apply & Form Filler"**.

---

## 🎯 How to Use on Job Portals

### 1. LinkedIn Easy Apply
1. Go to any LinkedIn job with the **"Easy Apply"** button.
2. Click **Easy Apply**.
3. In the floating widget on the bottom-right, click **"⚡ Auto-Fill Application (1-Click)"**.
4. The tool automatically fills your contact info, total experience (2.5), selects "Yes" for authorization, and handles radio buttons.
5. Click **Next** / **Review** -> **Submit**!

### 2. Naukri & Indeed
1. Open any job application modal or questionnaire.
2. Click the floating **"🤖 AI Auto-Fill"** button or click the extension icon in your toolbar.
3. Review the green-highlighted fields and submit.

### 3. Greenhouse (`boards.greenhouse.io`) & Lever (`jobs.lever.co`)
1. Open the application form.
2. Click **"⚡ Auto-Fill Application"**.
3. All personal details, URLs (LinkedIn, GitHub, Portfolio), and current employment fields are filled in less than 1 second.
4. Click **"📝 Insert Tailored Cover Letter / Pitch"** to fill the cover letter textarea.
5. Attach your resume PDF from `c:\Users\DELL\Desktop\30Days-leraning\ai-job-search\cv\main_example.pdf` and submit!

---

## ⚙️ Customizing Profile Data
To modify your contact info, notice period, or salary expectations, edit:
- [`tools/chrome_extension/content.js`](content.js)
- [`tools/chrome_extension/profile.json`](profile.json)
After editing, simply click the **Reload (🔄)** icon on the extension in `chrome://extensions/`.
