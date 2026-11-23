// =========================================================================
// AI Job Auto-Apply & Form Auto-Filler Content Script
// Tailored for Roshan Moger (2.5+ Years Full Stack Developer)
// Supports: LinkedIn Easy Apply, Naukri, Indeed, Greenhouse, Lever, Workday & Generic ATS
// =========================================================================

const CANDIDATE = {
  fullName: "Roshan Moger",
  firstName: "Roshan",
  lastName: "Moger",
  email: "roshanmoger502@gmail.com",
  phone: "+91-8970035508",
  cleanPhone: "8970035508",
  city: "Mysore",
  state: "Karnataka",
  country: "India",
  location: "Mysore, Karnataka, India",
  preferredLocation: "Bengaluru, Karnataka, India",
  experienceYears: "2.5",
  headline: "Full Stack Developer (2.5+ Yrs) | React.js | TypeScript | ASP.NET Core | C# | AWS | MCP | Generative AI",
  linkedin: "https://linkedin.com/in/roshan-moger",
  github: "https://github.com/Roshan-moger",
  portfolio: "https://roshan-devhub.netlify.app",
  currentCompany: "ExcelSoft Technologies",
  currentRole: "Associate Software Engineer",
  noticePeriod: "15 to 30 Days",
  noticePeriodDays: "30",
  currentCTC: "Negotiable",
  expectedCTC: "12-16 LPA",
  education: {
    degree: "Bachelor of Engineering (B.E.)",
    institution: "NIE Institute of Technology, Mysore",
    major: "Electrical & Electronics Engineering",
    graduationYear: "2023",
    gpa: "7.8"
  },
  skills: [
    "React.js", "TypeScript", "JavaScript", "ASP.NET Core", "C#", "REST APIs",
    "Model Context Protocol (MCP)", "AWS Bedrock", "Google Gemini",
    "Redux", "Tailwind CSS", "Redis", "WebSockets", "Docker", "Kubernetes",
    "AWS", "PostgreSQL", "MongoDB", "SQL Server", "Node.js", "Express.js"
  ],
  coverLetter: `Dear Hiring Team,

I am writing to express my strong interest in this engineering role. With 2.5+ years of full-stack software development experience at ExcelSoft Technologies, I specialize in building responsive React.js/TypeScript web applications and robust ASP.NET Core / C# backend microservices.

Recently, I designed and deployed a Model Context Protocol (MCP) server in .NET to expose SaaS workflows to AI systems, and engineered an in-product conversational assistant integrating Google Gemini via AWS Bedrock. Additionally, I implemented high-throughput Redis caching to cut database bottlenecks and built real-time WebSocket telemetry systems.

I would welcome the opportunity to bring my full-stack and AI-integration expertise to your engineering team.

Best regards,
Roshan Moger
+91-8970035508 | roshanmoger502@gmail.com
Portfolio: https://roshan-devhub.netlify.app
LinkedIn: https://linkedin.com/in/roshan-moger`
};

// --- SIMULATE USER INPUT (Crucial for React / Angular / Vue state updates) ---
function setNativeValue(element, value) {
  if (!element) return;
  const valueSetter = Object.getOwnPropertyDescriptor(element, 'value') ?
                      Object.getOwnPropertyDescriptor(element, 'value').set : null;
  const prototype = Object.getPrototypeOf(element);
  const prototypeValueSetter = Object.getOwnPropertyDescriptor(prototype, 'value') ?
                               Object.getOwnPropertyDescriptor(prototype, 'value').set : null;

  if (prototypeValueSetter && valueSetter !== prototypeValueSetter) {
    prototypeValueSetter.call(element, value);
  } else if (valueSetter) {
    valueSetter.call(element, value);
  } else {
    element.value = value;
  }

  // Dispatch full event sequence
  element.dispatchEvent(new Event('input', { bubbles: true, cancelable: true }));
  element.dispatchEvent(new Event('change', { bubbles: true, cancelable: true }));
  element.dispatchEvent(new Event('blur', { bubbles: true, cancelable: true }));
  
  // Highlight visually
  element.classList.add("ai-autofilled-field");
}

// --- FIELD HEURISTIC MATCHER ---
function getFieldLabelText(input) {
  let text = "";
  // 1. Direct label
  if (input.labels && input.labels.length > 0) {
    text += " " + Array.from(input.labels).map(l => l.innerText).join(" ");
  }
  // 2. aria-labelledby
  const labelledBy = input.getAttribute("aria-labelledby");
  if (labelledBy) {
    const el = document.getElementById(labelledBy);
    if (el) text += " " + el.innerText;
  }
  // 3. aria-label
  if (input.getAttribute("aria-label")) text += " " + input.getAttribute("aria-label");
  // 4. placeholder, name, id, data-automation-id
  if (input.placeholder) text += " " + input.placeholder;
  if (input.name) text += " " + input.name;
  if (input.id) text += " " + input.id;
  if (input.getAttribute("data-automation-id")) text += " " + input.getAttribute("data-automation-id");

  // 5. Closest parent label or legend
  const parentLabel = input.closest("label, .form-group, .field, [class*='form-item'], [class*='input-container']");
  if (parentLabel) text += " " + parentLabel.innerText;

  return text.toLowerCase().trim();
}

// --- MAIN AUTO-FILL ENGINE ---
function runAutoFill() {
  let filledCount = 0;
  const inputs = document.querySelectorAll("input, textarea, select");

  inputs.forEach(el => {
    // Skip hidden or disabled inputs
    if (el.type === "hidden" || el.disabled || el.readOnly || el.style.display === "none") return;
    const desc = getFieldLabelText(el);

    // 1. FIRST NAME
    if (/first[\s_-]?name|given[\s_-]?name|fname/i.test(desc) && !/last|full/i.test(desc)) {
      setNativeValue(el, CANDIDATE.firstName);
      filledCount++;
      return;
    }

    // 2. LAST NAME / SURNAME
    if (/last[\s_-]?name|sur[\s_-]?name|family[\s_-]?name|lname/i.test(desc)) {
      setNativeValue(el, CANDIDATE.lastName);
      filledCount++;
      return;
    }

    // 3. FULL NAME
    if (/full[\s_-]?name|candidate[\s_-]?name|your[\s_-]?name|^name$/i.test(desc) && !/company|file|role/i.test(desc)) {
      setNativeValue(el, CANDIDATE.fullName);
      filledCount++;
      return;
    }

    // 4. EMAIL ADDRESS
    if (/email|e-mail/i.test(desc) || el.type === "email") {
      setNativeValue(el, CANDIDATE.email);
      filledCount++;
      return;
    }

    // 5. PHONE / MOBILE
    if (/phone|mobile|contact[\s_-]?number|cell/i.test(desc) || el.type === "tel") {
      setNativeValue(el, CANDIDATE.phone);
      filledCount++;
      return;
    }

    // 6. LINKEDIN URL
    if (/linkedin/i.test(desc)) {
      setNativeValue(el, CANDIDATE.linkedin);
      filledCount++;
      return;
    }

    // 7. GITHUB URL
    if (/github/i.test(desc)) {
      setNativeValue(el, CANDIDATE.github);
      filledCount++;
      return;
    }

    // 8. PORTFOLIO / WEBSITE
    if (/portfolio|website|personal[\s_-]?url|webpage/i.test(desc)) {
      setNativeValue(el, CANDIDATE.portfolio);
      filledCount++;
      return;
    }

    // 9. CURRENT COMPANY / EMPLOYER
    if (/current[\s_-]?(?:company|employer|organization)|present[\s_-]?(?:company|employer)/i.test(desc)) {
      setNativeValue(el, CANDIDATE.currentCompany);
      filledCount++;
      return;
    }

    // 10. CURRENT JOB TITLE / DESIGNATION
    if (/current[\s_-]?(?:job[\s_-]?title|title|role|designation)/i.test(desc)) {
      setNativeValue(el, CANDIDATE.currentRole);
      filledCount++;
      return;
    }

    // 11. LOCATION / CITY
    if (/(?:current[\s_-]?)?city|location|current[\s_-]?address/i.test(desc) && !/state|country|zip|postal/i.test(desc)) {
      setNativeValue(el, CANDIDATE.location);
      filledCount++;
      return;
    }

    // 12. TOTAL YEARS OF EXPERIENCE
    if (/total[\s_-]?(?:years[\s_-]?of[\s_-]?)?experience|years[\s_-]?(?:of[\s_-]?)?exp|relevant[\s_-]?experience/i.test(desc)) {
      if (el.tagName === "SELECT") {
        selectDropdownOption(el, ["2", "2.5", "2+", "1-3", "2-3", "2 to 3", "3"]);
      } else {
        setNativeValue(el, CANDIDATE.experienceYears);
      }
      filledCount++;
      return;
    }

    // 13. NOTICE PERIOD
    if (/notice[\s_-]?period|serving[\s_-]?notice|how[\s_-]?soon[\s_-]?can[\s_-]?you[\s_-]?join/i.test(desc)) {
      if (el.tagName === "SELECT") {
        selectDropdownOption(el, ["immediate", "15", "30", "1 month", "15-30"]);
      } else {
        setNativeValue(el, CANDIDATE.noticePeriod);
      }
      filledCount++;
      return;
    }

    // 14. CURRENT CTC & EXPECTED CTC
    if (/current[\s_-]?(?:ctc|salary|compensation|annual[\s_-]?salary)/i.test(desc)) {
      setNativeValue(el, CANDIDATE.currentCTC);
      filledCount++;
      return;
    }
    if (/expected[\s_-]?(?:ctc|salary|compensation)/i.test(desc)) {
      setNativeValue(el, CANDIDATE.expectedCTC);
      filledCount++;
      return;
    }

    // 15. COVER LETTER / WHY HIRE YOU / SUMMARY
    if (el.tagName === "TEXTAREA" && /cover[\s_-]?letter|why[\s_-]?(?:should[\s_-]?we[\s_-]?hire|are[\s_-]?you[\s_-]?interested)|summary|tell[\s_-]?us[\s_-]?about/i.test(desc)) {
      setNativeValue(el, CANDIDATE.coverLetter);
      filledCount++;
      return;
    }

    // 16. RADIO BUTTONS & CHECKBOXES (Work authorization & sponsorship)
    if (el.type === "radio" || el.type === "checkbox") {
      const radioDesc = desc;
      // "Are you authorized to work in India?" -> Yes
      if (/authorized[\s_-]?to[\s_-]?work|legally[\s_-]?authorized/i.test(radioDesc)) {
        if (/yes|true|authorized/i.test(el.value) || /yes/i.test(radioDesc)) {
          el.checked = true;
          el.dispatchEvent(new Event('change', { bubbles: true }));
          filledCount++;
        }
      }
      // "Do you require sponsorship?" -> No
      if (/require[\s_-]?sponsorship|need[\s_-]?sponsorship|visa[\s_-]?sponsorship/i.test(radioDesc)) {
        if (/no|false|not/i.test(el.value) || /no/i.test(radioDesc)) {
          el.checked = true;
          el.dispatchEvent(new Event('change', { bubbles: true }));
          filledCount++;
        }
      }
    }
  });

  // Handle LinkedIn Easy Apply multi-step modal specifically
  handleLinkedInEasyApply();

  return filledCount;
}

// --- DROPDOWN SELECT HELPER ---
function selectDropdownOption(selectEl, searchTerms) {
  for (let i = 0; i < selectEl.options.length; i++) {
    const optText = selectEl.options[i].text.toLowerCase();
    const optVal = selectEl.options[i].value.toLowerCase();
    for (const term of searchTerms) {
      if (optText.includes(term.toLowerCase()) || optVal.includes(term.toLowerCase())) {
        selectEl.selectedIndex = i;
        selectEl.dispatchEvent(new Event('change', { bubbles: true }));
        selectEl.classList.add("ai-autofilled-field");
        return true;
      }
    }
  }
  return false;
}

// --- LINKEDIN EASY APPLY SPECIALIZED HANDLER ---
function handleLinkedInEasyApply() {
  const modal = document.querySelector(".jobs-easy-apply-modal, .artdeco-modal");
  if (!modal) return;

  // Answer LinkedIn radio questions: Yes to authorization, No to sponsorship
  const radioGroups = modal.querySelectorAll("fieldset");
  radioGroups.forEach(fieldset => {
    const legendText = fieldset.innerText.toLowerCase();
    const radios = fieldset.querySelectorAll("input[type='radio']");
    if (radios.length >= 2) {
      if (legendText.includes("authorized") || legendText.includes("legally")) {
        // Select Yes
        for (const r of radios) {
          if (r.value === "Yes" || r.id.toLowerCase().includes("yes") || r.closest("label").innerText.toLowerCase().includes("yes")) {
            r.checked = true;
            r.dispatchEvent(new Event('change', { bubbles: true }));
            r.classList.add("ai-autofilled-field");
            break;
          }
        }
      } else if (legendText.includes("sponsorship") || legendText.includes("visa")) {
        // Select No
        for (const r of radios) {
          if (r.value === "No" || r.id.toLowerCase().includes("no") || r.closest("label").innerText.toLowerCase().includes("no")) {
            r.checked = true;
            r.dispatchEvent(new Event('change', { bubbles: true }));
            r.classList.add("ai-autofilled-field");
            break;
          }
        }
      }
    }
  });
}

// --- INJECT IN-PAGE FLOATING HUD WIDGET ---
function injectFloatingHUD() {
  if (document.getElementById("ai-apply-widget-container")) return;

  const container = document.createElement("div");
  container.id = "ai-apply-widget-container";
  container.innerHTML = `
    <div id="aiApplyTrigger" class="ai-apply-trigger-btn">
      <span class="ai-apply-pulse"></span>
      <span>🤖 AI Auto-Fill</span>
    </div>

    <div id="aiApplyCard" class="ai-apply-card" style="display: none;">
      <div class="ai-card-header">
        <div>
          <div class="ai-card-title">⚡ AI Application Auto-Filler</div>
          <div class="ai-card-sub">Roshan Moger • 2.5+ Yrs Full Stack</div>
        </div>
        <button id="aiCardClose" class="ai-card-close" title="Minimize">&times;</button>
      </div>

      <button id="btnAutoFillNow" class="ai-btn-primary">
        <span>⚡ Auto-Fill Application (1-Click)</span>
      </button>

      <button id="btnInsertCoverLetter" class="ai-btn-secondary">
        <span>📝 Insert Tailored Cover Letter / Pitch</span>
      </button>

      <div class="ai-quick-copy-grid">
        <div class="ai-copy-pill" id="copyPhone" title="Click to copy Phone">📞 Copy Phone</div>
        <div class="ai-copy-pill" id="copyEmail" title="Click to copy Email">📧 Copy Email</div>
        <div class="ai-copy-pill" id="copyPortfolio" title="Click to copy Portfolio">🌐 Copy Portfolio</div>
        <div class="ai-copy-pill" id="copyLinkedIn" title="Click to copy LinkedIn">🔗 Copy LinkedIn</div>
      </div>

      <div id="aiStatusMsg" class="ai-status-msg">
        Ready to auto-fill form fields on this page.
      </div>
    </div>
  `;

  document.body.appendChild(container);

  // Event Listeners
  const trigger = container.querySelector("#aiApplyTrigger");
  const card = container.querySelector("#aiApplyCard");
  const closeBtn = container.querySelector("#aiCardClose");
  const fillBtn = container.querySelector("#btnAutoFillNow");
  const coverBtn = container.querySelector("#btnInsertCoverLetter");
  const statusMsg = container.querySelector("#aiStatusMsg");

  trigger.addEventListener("click", () => {
    trigger.style.display = "none";
    card.style.display = "flex";
  });

  closeBtn.addEventListener("click", () => {
    card.style.display = "none";
    trigger.style.display = "flex";
  });

  fillBtn.addEventListener("click", () => {
    const count = runAutoFill();
    statusMsg.className = "ai-status-msg success";
    statusMsg.innerText = `🎉 Successfully filled ${count} field(s)! Please review before submitting.`;
  });

  coverBtn.addEventListener("click", () => {
    const textareas = document.querySelectorAll("textarea");
    if (textareas.length > 0) {
      setNativeValue(textareas[0], CANDIDATE.coverLetter);
      statusMsg.className = "ai-status-msg success";
      statusMsg.innerText = "✅ Tailored cover letter inserted into textarea!";
    } else {
      navigator.clipboard.writeText(CANDIDATE.coverLetter);
      statusMsg.className = "ai-status-msg";
      statusMsg.innerText = "📋 No textarea found. Cover letter copied to clipboard!";
    }
  });

  // Quick Copy buttons
  container.querySelector("#copyPhone").addEventListener("click", () => {
    navigator.clipboard.writeText(CANDIDATE.phone);
    statusMsg.innerText = "📞 Phone copied (+91-8970035508)!";
  });
  container.querySelector("#copyEmail").addEventListener("click", () => {
    navigator.clipboard.writeText(CANDIDATE.email);
    statusMsg.innerText = "📧 Email copied (roshanmoger502@gmail.com)!";
  });
  container.querySelector("#copyPortfolio").addEventListener("click", () => {
    navigator.clipboard.writeText(CANDIDATE.portfolio);
    statusMsg.innerText = "🌐 Portfolio URL copied!";
  });
  container.querySelector("#copyLinkedIn").addEventListener("click", () => {
    navigator.clipboard.writeText(CANDIDATE.linkedin);
    statusMsg.innerText = "🔗 LinkedIn URL copied!";
  });
}

// --- LISTEN FOR MESSAGES FROM POPUP ---
chrome.runtime.onMessage?.addListener((request, sender, sendResponse) => {
  if (request.action === "autofill") {
    const count = runAutoFill();
    sendResponse({ status: "success", count: count });
  } else if (request.action === "copy_cover") {
    navigator.clipboard.writeText(CANDIDATE.coverLetter);
    sendResponse({ status: "copied" });
  }
});

// Auto-inject HUD when page loads
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", injectFloatingHUD);
} else {
  injectFloatingHUD();
}
