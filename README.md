// ────────────────────────────────────────────────
//  API KEYS – Load from localStorage or prompt once
// ────────────────────────────────────────────────
let ANTHROPIC_API_KEY = localStorage.getItem('claudeKey');

if (!ANTHROPIC_API_KEY) {
  ANTHROPIC_API_KEY = prompt("Enter your Claude API key (only once - saved in browser):");
  if (ANTHROPIC_API_KEY && ANTHROPIC_API_KEY.trim() !== '') {
    localStorage.setItem('claudeKey', ANTHROPIC_API_KEY.trim());
    alert("Claude API key saved in your browser storage for future use.");
  } else {
    alert("No key entered — Claude features will be disabled.");
    ANTHROPIC_API_KEY = null; // disable Claude
  }
}

// Optional: Do the same for other keys if you want them prompted too
let GEMINI_API_KEY = localStorage.getItem('geminiKey');
if (!GEMINI_API_KEY) {
  GEMINI_API_KEY = prompt("Enter your Gemini API key (optional - for backup):");
  if (GEMINI_API_KEY && GEMINI_API_KEY.trim() !== '') {
    localStorage.setItem('geminiKey', GEMINI_API_KEY.trim());
    alert("Gemini API key saved.");
  } else {
    GEMINI_API_[index.html](https://github.com/user-attachments/files/26071826/index.html)
KEY = null;
  }
}

const COMIC_VINE_API_KEY = 'your-comic-vine-key-here';      // still hard-code if you prefer
const SUPERHERO_TOKEN    = 'your-superhero-api-token-here'; // or prompt similarly

// ────────────────────────────────────────────────
// Rest of your script continues here...
// (scanner functions, getAIValue, renderCollection, etc.)

  let scanner = null;
  let comics = JSON.parse(localStorage.getItem('comics')) || [];
  let doubleCheckAI = false;  // Toggle for running both AIs

  // ────────────────────────────────────────────────
  //  Toggle Double-Check Mode
  // ────────────────────────────────────────────────
  function toggleDoubleCheck() {
    doubleCheckAI = !doubleCheckAI;
    alert(doubleCheckAI 
      ? "Double-check ON: Both Claude and Gemini will run on next scan."
      : "Double-check OFF: Using Claude primary + Gemini fallback.");
  }

  // ────────────────────────────────────────────────
  //  Scanner Setup (unchanged)
  // ────────────────────────────────────────────────
  function startScanner() {
    if (scanner) return;
    scanner = new Html5Qrcode("reader");
    scanner.start({ facingMode: "environment" }, { fps: 10, qrbox: 250 }, onScanSuccess, ()=>{})
      .catch(err => alert("Camera error: " + err));
  }

  function stopScanner() {
    if (scanner) scanner.stop().then(() => scanner = null);
  }

  // ────────────────────────────────────────────────
  //  Scan Success – Main Flow
  // ────────────────────────────────────────────────
  async function onScanSuccess(decodedText) {
    stopScanner();
    document.getElementById('result').innerHTML = `Barcode: ${decodedText}<br>Capturing photo...`;

    // Capture photo
    const video = document.querySelector('video');
    let photoDataUrl = '';
    if (video) {
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext('2d').drawImage(video, 0, 0);
      photoDataUrl = canvas.toDataURL('image/jpeg');
    }

    // User confirms/edits
    const title  = prompt("Comic Title:", "Unknown") || "Unknown";
    const issue  = prompt("Issue #:", "1") || "1";
    const grade  = prompt("Grade (VF/NM/etc):", "NM") || "NM";

    // Comic Vine metadata
    const cvData = await comicVineLookup(title, issue);
    const finalTitle = cvData?.volume?.name || title;
    const finalIssue = cvData?.issue_number || issue;
    const finalYear  = cvData?.cover_date?.split('-')[0] || new Date().getFullYear().toString();
    const coverUrl   = cvData?.image?.small_url || '';

    // SuperHero lookup
    let characterInfo = null;
    const possibleChar = finalTitle.split(" ")[0] || title.split(" ")[0];
    if (possibleChar) characterInfo = await getSuperheroInfo(possibleChar);

    // AI analysis – Claude primary + Gemini fallback (or double-check)
    let claudeResult = null;
    let geminiResult = null;

    // Always try Claude first
    claudeResult = await getClaudeValue(finalTitle, finalIssue, grade, photoDataUrl);

    // If double-check mode OR Claude failed/low, run Gemini
    if (doubleCheckAI || !claudeResult || claudeResult.mid_value <= 0) {
      geminiResult = await getGeminiValue(finalTitle, finalIssue, grade, photoDataUrl);
    }

    // Choose best result
    let aiResult = claudeResult && claudeResult.mid_value > 0 ? claudeResult : geminiResult || { mid_value: 0 };

    // Show both if double-check
    let resultDisplay = '';
    if (doubleCheckAI && claudeResult && geminiResult) {
      resultDisplay = `
        Claude: $${claudeResult.mid_value} (${claudeResult.suggested_grade}) – ${claudeResult.reason}<br>
        Gemini: $${geminiResult.mid_value} (${geminiResult.suggested_grade}) – ${geminiResult.reason}<br>
        Final: $${aiResult.mid_value} (${aiResult.suggested_grade})
      `;
    } else {
      resultDisplay = `Est. Value: $${aiResult.mid_value} (${aiResult.suggested_grade}) – ${aiResult.reason}`;
    }

    const newComic = {
      id: Date.now(),
      barcode: decodedText,
      title: finalTitle,
      issue: finalIssue,
      year: finalYear,
      grade: aiResult.suggested_grade || grade,
      photo: photoDataUrl || coverUrl,
      value: aiResult.mid_value || 0,
      status: determineStatus(aiResult.mid_value || 0),
      ai_reason: aiResult.reason || "No AI analysis",
      character: characterInfo?.name || null,
      powerstats: characterInfo?.powerstats || null,
      claude_value: claudeResult?.mid_value,
      gemini_value: geminiResult?.mid_value
    };

    comics.push(newComic);
    localStorage.setItem('comics', JSON.stringify(comics));
    renderCollection();

    document.getElementById('result').innerHTML = `
      <strong>${finalTitle} #${finalIssue} (${newComic.grade}) – ${finalYear}</strong><br>
      ${resultDisplay}<br>
      Status: <span class="status-${newComic.status.toLowerCase().replace(/ /g,'-')}">${newComic.status}</span><br>
      ${newComic.character ? `Character: ${newComic.character}` : ''}
      ${photoDataUrl ? `<br><img src="${photoDataUrl}" style="max-width:180px;border-radius:8px;margin-top:0.5rem;" />` : ''}
    `;
  }

  // ────────────────────────────────────────────────
  //  Status Logic – Balanced, no auto-keep everything
  // ────────────────────────────────────────────────
  function determineStatus(value) {
    if (value > 150) return "KEEP (High Value Key)";
    if (value > 50)  return "MONITOR / SELL INDIVIDUALLY";
    if (value > 20)  return "SELL INDIVIDUALLY";
    if (value < 10)  return "BUNDLE / SELL CHEAP";
    return "SELL INDIVIDUALLY";
  }

  // ────────────────────────────────────────────────
  //  Claude Analysis
  // ────────────────────────────────────────────────
  async function getClaudeValue(title, issue, grade, photoDataUrl) {
    if (!photoDataUrl) return null;
    try {
      const res = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': ANTHROPIC_API_KEY,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: "claude-3-5-sonnet-20241022",
          max_tokens: 300,
          messages: [{
            role: "user",
            content: [
              { type: "image", source: { type: "base64", media_type: "image/jpeg", data: photoDataUrl.split(',')[1] } },
              { type: "text", text: `Comic cover photo. Title: ${title} #${issue}, grade: ${grade}. 
Analyze condition (spine, corners, creases, gloss, color). Suggest raw grade + reasoning. 
Estimate realistic 2026 raw market value USD (low/mid/high) – do NOT lowball decent copies or keys. 
Return ONLY JSON: {"suggested_grade":"VF","reason":"short text","low":0,"mid":0,"high":0}` }
            ]
          }]
        })
      });

      if (!res.ok) throw new Error(res.status);
      const d = await res.json();
      const txt = d.content?.[0]?.text || '{}';
      const parsed = JSON.parse(txt);
      return parsed.mid ? { ...parsed, mid_value: parsed.mid } : null;
    } catch (e) {
      console.log("Claude failed:", e);
      return null;
    }
  }

  // ────────────────────────────────────────────────
  //  Gemini Analysis (Fallback or Double-Check)
  // ────────────────────────────────────────────────
  async function getGeminiValue(title, issue, grade, photoDataUrl) {
    if (!photoDataUrl) return null;
    try {
      const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEMINI_API_KEY}`, {
        method: 'POST',
        body: JSON.stringify({
          contents: [{
            parts: [
              { inline_data: { mime_type: "image/jpeg", data: photoDataUrl.split(',')[1] } },
              { text: `Comic cover. Title: ${title} #${issue}, grade: ${grade}. 
Analyze condition. Suggest raw grade + reasoning. 
Estimate realistic 2026 raw mid value USD – be fair, no lowballing. 
JSON only: {"suggested_grade":"VF","reason":"text","low":0,"mid":0,"high":0}` }
            ]
          }]
        })
      });

      const d = await res.json();
      const txt = d.candidates?.[0]?.content?.parts?.[0]?.text || '{}';
      const parsed = JSON.parse(txt);
      return parsed.mid ? { ...parsed, mid_value: parsed.mid } : null;
    } catch (e) {
      console.log("Gemini failed:", e);
      return null;
    }
  }

  // ────────────────────────────────────────────────
  //  Render Collection with Buttons & Override
  // ────────────────────────────────────────────────
  function renderCollection() {
    const list = document.getElementById('comic-list');
    list.innerHTML = '';
    comics.forEach(c => {
      const div = document.createElement('div');
      div.className = 'comic-card';
      div.innerHTML = `
        ${c.photo ? `<img src="${c.photo}" style="max-width:120px;border-radius:8px;float:left;margin-right:1rem;" />` : ''}
        <h3>${c.title} #${c.issue} (${c.year || '?'})</h3>
        <p>Grade: ${c.grade}</p>
        <p>Value: $${c.value.toFixed(0)}</p>
        <p>Status: <span class="status-${c.status.toLowerCase().replace(/ /g,'-')}">${c.status}</span></p>
        ${c.ai_reason ? `<p style="font-size:0.85rem;color:#aaa;">AI: ${c.ai_reason}</p>` : ''}
        ${c.character ? `<p>Character: ${c.character}</p>` : ''}
        <div style="margin-top:1rem;display:flex;gap:0.5rem;flex-wrap:wrap;">
          <button onclick="window.open('https://www.ebay.com/sch/i.html?_nkw=${encodeURIComponent(c.title + ' ' + c.issue + ' comic')}&_sacat=259104', '_blank')">eBay Search</button>
          <button onclick="window.open('https://comicvine.gamespot.com/search/?q=${encodeURIComponent(c.title + ' ' + c.issue)}', '_blank')">Comic Vine</button>
          <select onchange="updateStatus(${c.id}, this.value)" style="padding:0.5rem;">
            <option ${c.status === 'KEEP (High Value Key)' ? 'selected' : ''}>KEEP (High Value Key)</option>
            <option ${c.status === 'MONITOR / SELL INDIVIDUALLY' ? 'selected' : ''}>MONITOR / SELL INDIVIDUALLY</option>
            <option ${c.status === 'SELL INDIVIDUALLY' ? 'selected' : ''}>SELL INDIVIDUALLY</option>
            <option ${c.status === 'BUNDLE / SELL CHEAP' ? 'selected' : ''}>BUNDLE / SELL CHEAP</option>
          </select>
        </div>
        <div style="clear:both;"></div>
      `;
      list.appendChild(div);
    });
  }

  function updateStatus(id, newStatus) {
    const comic = comics.find(c => c.id === id);
    if (comic) {
      comic.status = newStatus;
      localStorage.setItem('comics', JSON.stringify(comics));
      renderCollection();
    }
  }

  // Load on start
  renderCollection();
</script>
