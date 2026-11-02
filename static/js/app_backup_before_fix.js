const incomeCategories = ["Salary","Business","Freelancing","Investment","Gift","Other Income"];
const expenseCategories = ["Food","Travel","Shopping","Education","Bills","Healthcare","Entertainment","Rent","Other Expense"];
let allTransactions = [];
let currentPage = "Dashboard";
const money = n => new Intl.NumberFormat("en-IN",{style:"currency",currency:"INR",maximumFractionDigits:2}).format(Number(n||0));

function toast(message) {
  const el = document.getElementById("toast");
  el.textContent = message; el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 2600);
}
function setPage(page) {
  currentPage = page;
  document.querySelectorAll(".nav-item").forEach(b => b.classList.toggle("active", b.dataset.page === page));
  if (page === "Add Transaction") {
    document.getElementById("transactionDialog").showModal();
    return;
  }
  renderPage();
}
document.querySelectorAll("[data-page]").forEach(b => b.addEventListener("click", () => setPage(b.dataset.page)));
document.getElementById("themeToggle").addEventListener("click", () => {
  document.body.classList.toggle("light-mode");
  toast(document.body.classList.contains("light-mode") ? "Light theme enabled" : "Dark theme enabled");
});
document.getElementById("closeDialog").onclick = () => document.getElementById("transactionDialog").close();
document.getElementById("cancelDialog").onclick = () => document.getElementById("transactionDialog").close();

function updateCategories() {
  const type = document.querySelector('input[name="type"]:checked').value;
  const cats = type === "Income" ? incomeCategories : expenseCategories;
  document.getElementById("category").innerHTML = cats.map(c => `<option>${c}</option>`).join("");
}
document.querySelectorAll('input[name="type"]').forEach(r => r.addEventListener("change", updateCategories));
updateCategories();

document.getElementById("transactionForm").addEventListener("submit", async e => {
  e.preventDefault();
  const type = document.querySelector('input[name="type"]:checked').value;
  const payload = {
    transaction_type: type,
    category: document.getElementById("category").value,
    amount: document.getElementById("amount").value,
    transaction_date: document.getElementById("transactionDate").value,
    description: document.getElementById("description").value
  };
  const msg = document.getElementById("formMessage");
  msg.textContent = "Saving…";
  try {
    const res = await fetch("/api/transactions", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Could not save transaction.");
    document.getElementById("transactionForm").reset();
    document.getElementById("transactionDate").value = new Date().toISOString().slice(0,10);
    document.querySelector('input[name="type"][value="Expense"]').checked = true;
    updateCategories();
    document.getElementById("transactionDialog").close();
    msg.textContent = "";
    await loadData(); setPage("Dashboard"); toast("Transaction saved successfully");
  } catch(err) { msg.textContent = err.message; }
});

async function loadData() {
  try {
    const res = await fetch("/api/transactions");

    if (!res.ok) {
      throw new Error("Could not load transactions.");
    }

    const data = await res.json();
    allTransactions = data.transactions || [];

    const s = data.summary || {};
    const incomeValue = document.getElementById("incomeValue");
    const expenseValue = document.getElementById("expenseValue");
    const savingsValue = document.getElementById("savingsValue");
    const savingsRate = document.getElementById("savingsRate");
    const ring = document.getElementById("savingsRing");
    const title = document.getElementById("insightTitle");
const text = document.getElementById("insightText");

if (title && text) {
  if (!allTransactions.length) {
    title.textContent = "Your journey starts here";
    text.textContent = "Add your first transaction to unlock financial insights.";
  } else if (s.savings < 0) {
    title.textContent = "Review your spending";
    text.textContent = `Your expenses exceed income by ${money(Math.abs(s.savings))}. Review your categories and spending habits.`;
  } else if (s.income > 0 && s.savings_rate >= 30) {
    title.textContent = "You're building momentum";
    text.textContent = `You're retaining ${Number(s.savings_rate).toFixed(1)}% of recorded income. Keep tracking consistently.`;
  } else if (s.income > 0) {
    title.textContent = "Find room to save";
    text.textContent = `Your savings rate is ${Number(s.savings_rate).toFixed(1)}%. Explore your spending breakdown for opportunities.`;
  } else {
    title.textContent = "Track your money";
    text.textContent = "Add an income transaction to calculate your savings rate.";
  }
}

// Draw dashboard charts only when the dashboard is visible.
    if (currentPage === "Dashboard") {
      if (document.getElementById("donutChart") &&
          document.getElementById("trendChart")) {
        drawCharts();
      }

      if (document.getElementById("recentTable")) {
        renderRecent(allTransactions.slice(0, 5));
      }
    }
  } catch (error) {
    console.error("FinTrack data loading error:", error);
    toast("Unable to refresh financial data. Please try again.");
  }
}
async function loadData() 
{
  const res = await fetch("/api/transactions");
  const data = await res.json();
  allTransactions = data.transactions || [];
  const s = data.summary || {};
  const incomeEl = document.getElementById("incomeValue");
  const expenseEl = document.getElementById("expenseValue");
  const savingsEl = document.getElementById("savingsValue");
  const rateEl = document.getElementById("savingsRate");
  const ring = document.getElementById("savingsRing");

  if (incomeEl) incomeEl.textContent = money(s.income);
  if (expenseEl) expenseEl.textContent = money(s.expenses);
  if (savingsEl) savingsEl.textContent = money(s.savings);

  const rate = Math.max(0, Math.min(100, Number(s.savings_rate || 0)));

  if (rateEl) rateEl.textContent = `${rate.toFixed(1)}%`;
  if (ring) {
    ring.style.background =
      `conic-gradient(#1adba4 ${rate}%, #223246 ${rate}% 100%)`;
    ring.style.borderColor = "transparent";
    ring.style.backgroundClip = "padding-box";
  }
const title = document.getElementById("insightTitle");
const text = document.getElementById("insightText");

if (title && text) {
  if (!allTransactions.length) {
    title.textContent = "Your journey starts here";
    text.textContent = "Add your first transaction to unlock financial 
insights.";
  } else if (s.savings < 0) {
    title.textContent = "Review your spending";
    text.textContent = `Your expenses exceed income by 
${money(Math.abs(s.savings))}. Review your categories and spending 
habits.`;
  } else if (s.income > 0 && s.savings_rate >= 30) {
    title.textContent = "You're building momentum";
    text.textContent = `You're retaining 
${Number(s.savings_rate).toFixed(1)}% of recorded income. Keep tracking 
consistently.`;
  } else if (s.income > 0) {
    title.textContent = "Find room to save";
    text.textContent = `Your savings rate is 
${Number(s.savings_rate).toFixed(1)}%. Explore your spending breakdown for 
opportunities.`;
  } else {
    title.textContent = "Track your money";
    text.textContent = "Add an income transaction to calculate your 
savings rate.";
  }
}
 text.textContent = `Your savings rate is 
${Number(s.savings_rate).toFixed(1)}%. Explore your spending breakdown for 
opportunities.`;
} else {
  title.textContent = "Track your money";
  text.textContent = "Add an income transaction to calculate your savings 
rate.";
}
}

drawCharts();
renderRecent(allTransactions.slice(0, 5)); drawCharts();
  renderRecent(allTransactions.slice(0,5));
}
function drawSparkline(id,color,seed) {
  const vals = Array.from({length:12},(_,i)=>Math.max(2,Math.sin(i*.9+seed)*10+i*2+5));
  const points = vals.map((v,i)=>`${i*10},${40-v*2}`).join(" ");
  document.getElementById(id).innerHTML = `<svg viewBox="0 0 110 48" preserveAspectRatio="none" width="100%" height="100%"><polyline points="${points}" fill="none" stroke="${color}" stroke-width="2.2" vector-effect="non-scaling-stroke"/></svg>`;
}
function drawCharts() {
  drawSparkline("sparkIncome","#30efb4",1);
  drawSparkline("sparkExpense","#ff668c",3);
  drawSparkline("sparkSavings","#b06cff",2);
  const expenses = allTransactions.filter(t=>t.transaction_type==="Expense");
  const catMap = {};
  expenses.forEach(t=>catMap[t.category]=(catMap[t.category]||0)+Number(t.amount));
  const labels = Object.keys(catMap), values = labels.map(k=>catMap[k]);
  const common = {paper_bgcolor:"rgba(0,0,0,0)",plot_bgcolor:"rgba(0,0,0,0)",font:{family:"DM Sans",color:"#c1cfde",size:11},margin:{l:8,r:8,t:12,b:8},showlegend:true,legend:{orientation:"h",y:-.12,font:{size:10}}};
  Plotly.react("donutChart", values.length ? [{type:"pie",labels,values,hole:.68,sort:false,textinfo:"percent",textposition:"inside",marker:{colors:["#20e5aa","#4abef4","#a56cff","#ff668c","#ffc45e","#76e5c5","#f58b47"],line:{color:"#0d1826",width:3}},hovertemplate:"%{label}<br>₹%{value:,.2f}<extra></extra>"}] : [], {...common,annotations:values.length?[{text:`<b>${money(values.reduce((a,b)=>a+b,0))}</b><br><span style="font-size:10px">Expenses</span>`,showarrow:false,font:{size:16,color:"#f3f8ff"}}]:[]}, {displayModeBar:false,responsive:true});
  const income = allTransactions.filter(t=>t.transaction_type==="Income").reduce((a,t)=>a+Number(t.amount),0);
  const expense = expenses.reduce((a,t)=>a+Number(t.amount),0);
  Plotly.react("trendChart",[
    {x:["Income","Expenses"],y:[income,expense],type:"bar",marker:{color:["#30efb4","#b06cff"],line:{width:0}},text:[money(income),money(expense)],textposition:"outside",hovertemplate:"%{x}<br>₹%{y:,.2f}<extra></extra>"}
  ],{...common,showlegend:false,margin:{l:48,r:12,t:20,b:35},yaxis:{gridcolor:"rgba(145,164,187,.12)",zeroline:false,tickprefix:"₹"},xaxis:{showgrid:false}}, {displayModeBar:false,responsive:true});
}
function renderRecent(rows) {
  const el = document.getElementById("recentTable");
  if (!rows.length) { el.innerHTML='<div class="empty-state">✦<br>No transactions yet.<br>Add your first transaction to get started.</div>'; return; }
  el.innerHTML = `<div class="table-wrap"><table><thead><tr><th>DATE</th><th>TYPE</th><th>CATEGORY</th><th>AMOUNT</th><th>DESCRIPTION</th></tr></thead><tbody>${rows.map(t=>`<tr><td>${escapeHtml(t.transaction_date)}</td><td><span class="badge ${t.transaction_type==="Income"?"income":"expense"}">${escapeHtml(t.transaction_type)}</span></td><td>${escapeHtml(t.category)}</td><td class="${t.transaction_type==="Income"?"amount-income":"amount-expense"}">${t.transaction_type==="Income"?"+":"−"} ${money(t.amount)}</td><td>${escapeHtml(t.description||"—")}</td></tr>`).join("")}</tbody></table></div>`;
}
function escapeHtml(value) { return String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
function renderPage() {
  const content = document.getElementById("pageContent");
  if (currentPage==="Dashboard") {
    content.style.display="";
    loadData();
    return;
  }
  content.style.display="";
  const head = `<div class="page-title">${escapeHtml(currentPage)}</div><p class="page-subtitle">Your FinTrack workspace · Data is saved in your local SQLite database.</p>`;
  if (currentPage==="Transaction History") {
    content.innerHTML = head + `<section class="panel"><div class="panel-head"><div><h3>All transactions</h3><p>Review or remove a record.</p></div><button class="primary-btn" id="addFromHistory">＋ Add transaction</button></div><div id="historyTable"></div></section>`;
    document.getElementById("addFromHistory").onclick=()=>setPage("Add Transaction");
    renderHistory(allTransactions); return;
  }
  if (currentPage==="Analytics") {
    const totalIncome=allTransactions.filter(t=>t.transaction_type==="Income").reduce((a,t)=>a+Number(t.amount),0);
    const totalExpense=allTransactions.filter(t=>t.transaction_type==="Expense").reduce((a,t)=>a+Number(t.amount),0);
    content.innerHTML=head+`<div class="metrics"><article class="metric-card income-card"><div class="metric-label">TOTAL INCOME</div><strong>${money(totalIncome)}</strong></article><article class="metric-card expense-card"><div class="metric-label">TOTAL EXPENSES</div><strong>${money(totalExpense)}</strong></article><article class="metric-card savings-card"><div class="metric-label">NET SAVINGS</div><strong>${money(totalIncome-totalExpense)}</strong></article></div><br><section class="panel"><h3>Income vs expenses</h3><div id="analyticsChart" class="chart"></div></section>`;
    Plotly.react("analyticsChart",[{x:["Income","Expenses"],y:[totalIncome,totalExpense],type:"bar",marker:{color:["#30efb4","#b06cff"]}}],{paper_bgcolor:"rgba(0,0,0,0)",plot_bgcolor:"rgba(0,0,0,0)",font:{color:"#c1cfde"},yaxis:{gridcolor:"#243344"},showlegend:false},{displayModeBar:false,responsive:true}); return;
  }
  if (currentPage==="Insights") {
    const expenses=allTransactions.filter(t=>t.transaction_type==="Expense");
    const sums={}; expenses.forEach(t=>sums[t.category]=(sums[t.category]||0)+Number(t.amount));
    const top=Object.entries(sums).sort((a,b)=>b[1]-a[1])[0];
    content.innerHTML=head+`<section class="panel"><div class="eyebrow">YOUR DATA, DECODED</div><h2>${top?`Highest spending category: ${escapeHtml(top[0])}`:"Start with your first transaction"}</h2><p class="page-subtitle">${top?`You've recorded ${money(top[1])} in ${escapeHtml(top[0])}. This is a summary of your entries, not financial advice.`:"Once you record income and expenses, this page highlights your largest spending category."}</p><p>Transactions recorded: <b>${allTransactions.length}</b></p></section>`; return;
  }
  if (currentPage==="About This Project") {
    content.innerHTML=head+`<section class="panel"><div class="eyebrow">COLLEGE PROJECT / PYTHON APPLICATION</div><h2>Personal finance, made visible.</h2><p class="page-subtitle">FinTrack records income and expenses, stores transactions, calculates summaries, and visualises spending.</p><div class="metrics"><article class="metric-card"><div class="metric-label">BACKEND</div><strong>Python + Flask</strong></article><article class="metric-card"><div class="metric-label">DATABASE</div><strong>SQLite</strong></article><article class="metric-card"><div class="metric-label">FRONTEND</div><strong>HTML / CSS / JS</strong></article></div><br><h3>How it works</h3><ol><li>HTML creates the page structure.</li><li>CSS styles the dark fintech interface.</li><li>JavaScript handles form interactions and charts.</li><li>Flask exposes API routes and validates transaction data.</li><li>SQLite stores transaction records using parameterised SQL.</li><li>Python calculates totals and savings; Plotly renders charts.</li></ol><h3>Key formulas</h3><pre>Total Income = sum of Income transactions\nTotal Expenses = sum of Expense transactions\nNet Savings = Total Income - Total Expenses\nSavings Rate = (Net Savings / Total Income) × 100</pre><p class="page-subtitle">This educational app does not connect to banks or provide regulated financial advice.</p></section>`; return;
  }
}
function renderHistory(rows) {
  const el=document.getElementById("historyTable");
  if (!rows.length) {el.innerHTML='<div class="empty-state">No transactions recorded yet.</div>';return;}
  el.innerHTML=`<div class="table-wrap"><table><thead><tr><th>DATE</th><th>TYPE</th><th>CATEGORY</th><th>AMOUNT</th><th>DESCRIPTION</th><th>ACTION</th></tr></thead><tbody>${rows.map(t=>`<tr><td>${escapeHtml(t.transaction_date)}</td><td><span class="badge ${t.transaction_type==="Income"?"income":"expense"}">${escapeHtml(t.transaction_type)}</span></td><td>${escapeHtml(t.category)}</td><td>${money(t.amount)}</td><td>${escapeHtml(t.description||"—")}</td><td><button class="secondary-btn delete-row" data-id="${Number(t.id)}">Delete</button></td></tr>`).join("")}</tbody></table></div>`;
  el.querySelectorAll(".delete-row").forEach(btn=>btn.addEventListener("click",async()=>{if(!confirm("Delete this transaction permanently?"))return;const res=await fetch(`/api/transactions/${btn.dataset.id}`,{method:"DELETE"});const data=await res.json();if(!res.ok){toast(data.error||"Delete failed");return;}await loadData();renderPage();toast("Transaction deleted");}));
}
document.getElementById("globalSearch").addEventListener("input",e=>{
  const q=e.target.value.trim().toLowerCase();
  if (!q) { if(currentPage==="Dashboard") renderRecent(allTransactions.slice(0,5)); return; }
  const found=allTransactions.filter(t=>[t.category,t.description,t.transaction_type,t.transaction_date].some(v=>String(v||"").toLowerCase().includes(q)));
  if(currentPage==="Dashboard")renderRecent(found.slice(0,8));
  else {currentPage="Transaction History";document.querySelectorAll(".nav-item").forEach(b=>b.classList.toggle("active",b.dataset.page===currentPage));document.getElementById("pageContent").innerHTML=`<div class="page-title">Search results</div><p class="page-subtitle">${found.length} matching transaction(s)</p><section class="panel" id="historyTable"></section>`;renderHistory(found);}
});
document.addEventListener("keydown",e=>{if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==="k"){e.preventDefault();document.getElementById("globalSearch").focus();}});
loadData();
