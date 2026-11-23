// AI Job Auto-Apply Popup Script
document.addEventListener("DOMContentLoaded", () => {
  const statusBox = document.getElementById("popupStatus");

  function setStatus(text, isSuccess = false) {
    if (!statusBox) return;
    statusBox.innerText = text;
    if (isSuccess) {
      statusBox.className = "status-box success";
    } else {
      statusBox.className = "status-box";
    }
  }

  // 1. Auto-Fill Current Application Page
  const fillBtn = document.getElementById("btnPopupAutoFill");
  if (fillBtn) {
    fillBtn.addEventListener("click", () => {
      setStatus("Analyzing page form fields...");
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (!tabs || !tabs[0]) {
          setStatus("Could not detect active tab.");
          return;
        }

        chrome.tabs.sendMessage(tabs[0].id, { action: "autofill" }, (response) => {
          if (chrome.runtime.lastError) {
            setStatus("Please reload this job page or ensure it's a web page.");
            return;
          }
          if (response && response.count !== undefined) {
            setStatus(`🎉 Filled ${response.count} field(s)! Review and submit.`, true);
          } else {
            setStatus("Form analyzed! Check highlighted fields.", true);
          }
        });
      });
    });
  }

  // 2. Copy AI-Tailored Cover Letter
  const coverBtn = document.getElementById("btnPopupCopyCover");
  if (coverBtn) {
    coverBtn.addEventListener("click", () => {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs && tabs[0]) {
          chrome.tabs.sendMessage(tabs[0].id, { action: "copy_cover" }, () => {});
        }
      });
      const coverLetterText = `Dear Hiring Team,

I am writing to express my strong interest in this engineering role. With 2.5+ years of full-stack software development experience at ExcelSoft Technologies, I specialize in building responsive React.js/TypeScript web applications and robust ASP.NET Core / C# backend microservices.

Recently, I designed and deployed a Model Context Protocol (MCP) server in .NET to expose SaaS workflows to AI systems, and engineered an in-product conversational assistant integrating Google Gemini via AWS Bedrock. Additionally, I implemented high-throughput Redis caching to cut database bottlenecks and built real-time WebSocket telemetry systems.

I would welcome the opportunity to bring my full-stack and AI-integration expertise to your engineering team.

Best regards,
Roshan Moger
+91-8970035508 | roshanmoger502@gmail.com
Portfolio: https://roshan-devhub.netlify.app
LinkedIn: https://linkedin.com/in/roshan-moger`;

      navigator.clipboard.writeText(coverLetterText).then(() => {
        setStatus("📋 Cover letter copied to clipboard!", true);
      }).catch(() => {
        setStatus("Could not copy automatically. Check permissions.");
      });
    });
  }

  // 3. Quick Copy Buttons
  const copyButtons = document.querySelectorAll(".copy-item");
  copyButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const val = btn.getAttribute("data-val");
      const label = btn.querySelector(".copy-label")?.innerText || "Item";
      if (val) {
        navigator.clipboard.writeText(val).then(() => {
          setStatus(`📋 ${label} copied to clipboard!`, true);
        });
      }
    });
  });

  // 4. Open Local Dashboard
  const dashBtn = document.getElementById("btnOpenDashboard");
  if (dashBtn) {
    dashBtn.addEventListener("click", () => {
      chrome.tabs.create({ url: "http://localhost:5000/reports/application-dashboard.html" });
    });
  }
});
