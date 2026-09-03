// Dynamic API base URL: works seamlessly on Render, localhost, or direct file preview
const API_BASE = (window.location.protocol === 'http:' || window.location.protocol === 'https:') 
    ? '' 
    : 'http://127.0.0.1:8000';

// Function to generate the main AI report and render charts
async function generateReport() {
    let daysInput = document.getElementById('days').value;
    let days = parseInt(daysInput, 10);
    if (isNaN(days) || days <= 0) {
        days = 30;
        document.getElementById('days').value = 30;
    }
    const loader = document.getElementById('loader');
    const reportContainer = document.getElementById('reportContainer');
    const aiOutput = document.getElementById('aiOutput');

    // Show loading spinner and hide the report container
    loader.classList.remove('hidden');
    reportContainer.classList.add('hidden');

    try {
        // Fetch data from the backend API
        const response = await fetch(`${API_BASE}/api/report?days=${days}`);
        const data = await response.json();

        if (data.status === "error") {
            loader.classList.add('hidden');
            reportContainer.classList.remove('hidden');
            document.getElementById('statDays').innerText = days;
            document.getElementById('statReviews').innerText = "0";
            aiOutput.innerHTML = `
                <div style="background: #fff5f5; border-left: 4px solid #f56565; color: #c53030; padding: 20px; border-radius: 8px;">
                    <h3 style="color:#c53030; margin-top:0;"><i class="fas fa-info-circle"></i> Notice</h3>
                    <p style="margin: 8px 0; color:#4a5568;">${data.message}</p>
                </div>`;
            return;
        }

        // ====================================================================
        // SMART AUTO-DETECT LOGIC (BULLETPROOF - UPDATED)
        // ====================================================================
        
        // 1. Fetch Report Text (Now matches 'report_html' from Python)
        const finalReport = data.report_html || data.ai_report || data.report || "Report data is missing from backend.";
        
        // 2. Fetch Total Reviews Count
        const finalTotal = data.total_reviews || 0;
        
        // 3. Fetch Sentiment Data safely (Now matches 'chart_data' from Python)
        const sData = data.chart_data || data.sentiment_counts || {};
        const posCount = sData.Positive || sData.positive || sData.Pos || 0;
        const neuCount = sData.Neutral || sData.neutral || sData.Neu || 0;
        const negCount = sData.Negative || sData.negative || sData.Neg || 0;

        // ====================================================================

        // Update UI text statistics
        document.getElementById('statDays').innerText = days;
        document.getElementById('statReviews').innerText = finalTotal;
        aiOutput.innerHTML = finalReport;

        // Check for an existing chart instance and destroy it to prevent canvas overlap errors
        let oldChart = Chart.getChart("sentimentChart");
        if (oldChart) {
            oldChart.destroy();
        }

        // Initialize the new chart on the cleared canvas using the safe data variables
        const ctx = document.getElementById('sentimentChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Positive', 'Neutral', 'Negative'],
                datasets: [{
                    label: 'Sentiment Breakdown',
                    data: [posCount, neuCount, negCount], // Using safe variables here
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.6)', // Green for Positive
                        'rgba(255, 206, 86, 0.6)', // Yellow for Neutral
                        'rgba(255, 99, 132, 0.6)'  // Red for Negative
                    ],
                    borderColor: [
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    }
                }
            }
        });

        // Hide loader and display the completed report
        loader.classList.add('hidden');
        reportContainer.classList.remove('hidden');

    } catch (error) {
        console.error("Error generating report:", error);
        loader.classList.add('hidden');
        alert("Failed to generate report. Please check if the backend server is running.");
    }
}

// Function to download the perfectly formatted report with Timeframe and Underlined Headings
function downloadPDF() {
    const element = document.getElementById('reportContainer');
    const aiOutput = document.getElementById('aiOutput');
    const actionArea = document.getElementById('actionArea');
    const statsBoxes = document.getElementById('statsBoxes');
    const chartCanvas = document.getElementById('sentimentChart'); 
    const chartParent = chartCanvas.parentElement; 
    
    // Get the number of days analyzed from the dashboard
    const analyzedDays = document.getElementById('statDays').innerText || document.getElementById('days').value;
    
    // 1. Temporarily save original HTML and styles
    const originalHTML = aiOutput.innerHTML; // Save original text
    const originalTextColor = aiOutput.style.color || '';
    const originalOverflow = aiOutput.style.overflow || '';
    const originalHeight = aiOutput.style.height || '';
    const originalMaxHeight = aiOutput.style.maxHeight || '';
    const originalElementHeight = element.style.height || '';
    
    // Save original chart parent styles
    const origParentBorder = chartParent.style.border || '';
    const origParentPadding = chartParent.style.padding || '';
    const origParentBg = chartParent.style.backgroundColor || '';
    const origParentRadius = chartParent.style.borderRadius || '';
    const origParentMargin = chartParent.style.marginBottom || '';
    const origParentHeight = chartParent.style.height || '';

    // 2. Hide unwanted items (Stats boxes & Buttons)
    if (statsBoxes) statsBoxes.style.display = 'none';
    actionArea.style.display = 'none';

    // 3. DYNAMIC MAIN HEADING
    const heading = document.createElement('h2');
    heading.id = 'pdfHeading';
    heading.innerText = 'E-Commerce AI Business Report';
    heading.style.textAlign = 'center';
    heading.style.color = '#000000';
    heading.style.paddingBottom = '10px';
    heading.style.marginBottom = '20px';
    heading.style.fontSize = '22px'; 
    heading.style.fontWeight = 'bold';
    heading.style.textTransform = 'uppercase'; 
    heading.style.borderBottom = '2px solid #000000'; 
    element.prepend(heading); 

    // 4. CHART IN A BOX 
    chartParent.style.border = '1px solid #ccc';
    chartParent.style.padding = '15px';
    chartParent.style.backgroundColor = '#fefefe';
    chartParent.style.borderRadius = '8px';
    chartParent.style.marginBottom = '25px'; 
    chartParent.style.height = 'auto'; 

    const originalChartHeight = chartCanvas.style.height || '';
    chartCanvas.style.height = '220px'; 

    let chart = Chart.getChart("sentimentChart");
    let originalChartColors = {};
    if (chart) {
        originalChartColors.x = chart.options.scales.x.ticks.color;
        originalChartColors.y = chart.options.scales.y.ticks.color;
        chart.options.scales.x.ticks.color = '#000000';
        chart.options.scales.x.ticks.font = { weight: 'bold', size: 12 };
        chart.options.scales.y.ticks.color = '#000000';
        chart.options.scales.y.ticks.font = { weight: 'bold', size: 12 };
        chart.resize(); 
        chart.update();
    }

    // 5. FORMAT THE TEXT REPORT (Inject Timeframe & CSS for Underlines)
    
    // Inject Timeframe exactly below "Overview" (or at the top if Overview is missing)
    const timeframeHTML = `<p style="font-size: 14px; font-weight: bold; color: #444; margin-bottom: 15px; text-transform: uppercase;">📅 Report Timeframe: Last ${analyzedDays} Days</p>`;
    if (originalHTML.includes('Overview')) {
        aiOutput.innerHTML = originalHTML.replace(/(<h[1-6].*?>Overview<\/h[1-6]>)/i, `$1\n${timeframeHTML}`);
    } else {
        aiOutput.innerHTML = timeframeHTML + originalHTML;
    }

    // Inject temporary CSS to underline all section headings (Overview, Customer Reviews, etc.)
    const pdfStyle = document.createElement('style');
    pdfStyle.id = 'pdfTempStyles';
    pdfStyle.innerHTML = `
        #aiOutput h1, #aiOutput h2, #aiOutput h3 {
            border-bottom: 2px solid #333 !important;
            padding-bottom: 6px !important;
            margin-bottom: 12px !important;
            margin-top: 20px !important;
            color: #000 !important;
        }
    `;
    document.head.appendChild(pdfStyle);

    aiOutput.style.color = '#000000';
    aiOutput.style.overflow = 'visible'; 
    aiOutput.style.height = 'max-content';      
    aiOutput.style.maxHeight = 'none';   
    aiOutput.style.lineHeight = '1.6'; 
    element.style.height = 'max-content';

    // 6. WAITING + GENERATE PDF
    setTimeout(() => {
        const opt = {
            margin:       [10, 15, 15, 15], 
            filename:     'AI_Business_Report_Pro.pdf',
            image:        { type: 'jpeg', quality: 1.0 },
            html2canvas:  { scale: 2, backgroundColor: '#ffffff', scrollY: 0 }, 
            jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' },
            pagebreak:    { mode: ['css', 'legacy'] } 
        };

        html2pdf().set(opt).from(element).save().then(() => {
            
            // ==============================================
            // RESTORE EVERYTHING 
            // ==============================================
            if (statsBoxes) statsBoxes.style.display = ''; 
            actionArea.style.display = 'flex';             
            
            const pdfHeading = document.getElementById('pdfHeading');
            if (pdfHeading) pdfHeading.remove();
            
            const tempStyles = document.getElementById('pdfTempStyles');
            if (tempStyles) tempStyles.remove();

            chartParent.style.border = origParentBorder;
            chartParent.style.padding = origParentPadding;
            chartParent.style.backgroundColor = origParentBg;
            chartParent.style.borderRadius = origParentRadius;
            chartParent.style.marginBottom = origParentMargin;
            chartParent.style.height = origParentHeight;

            aiOutput.innerHTML = originalHTML; // Remove timeframe text from screen UI
            aiOutput.style.color = originalTextColor;      
            aiOutput.style.overflow = originalOverflow;
            aiOutput.style.height = originalHeight;
            aiOutput.style.maxHeight = originalMaxHeight;
            aiOutput.style.lineHeight = ''; 
            element.style.height = originalElementHeight;
            
            chartCanvas.style.height = originalChartHeight;

            if (chart) {
                chart.options.scales.x.ticks.color = originalChartColors.x;
                chart.options.scales.x.ticks.font = { weight: 'normal', size: 12 };
                chart.options.scales.y.ticks.color = originalChartColors.y;
                chart.options.scales.y.ticks.font = { weight: 'normal', size: 12 };
                chart.resize(); 
                chart.update();
            }
        });
    }, 500);
}

// Function to handle interactive chat queries with the AI Agent
async function askChat() {
    const question = document.getElementById('chatInput').value.trim();
    let days = document.getElementById('days').value || 30;
    const chatReply = document.getElementById('chatReply');

    // Ensure the user has typed a question
    if (!question) {
        alert("Please enter a question first.");
        return;
    }

    // Display a temporary loading message in the chat box
    chatReply.innerHTML = "<em>AI is thinking and querying the database...</em>";

    try {
        // Send the user's question and timeframe to the backend chat API
        const response = await fetch(`${API_BASE}/api/chat?days=${days}&question=${encodeURIComponent(question)}`);
        const data = await response.json();
        
        // Display the final answer from the AI Agent
        chatReply.innerHTML = `<strong>AI:</strong> ${data.reply}`;
    } catch (error) {
        console.error("Chat error:", error);
        chatReply.innerHTML = `<span style="color: red;">Error connecting to AI. Make sure the server is running.</span>`;
    }
}

// Allow pressing Enter in chat input to ask question
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                askChat();
            }
        });
    }
});

// =======================================================
// AUTO-SAVE FEATURE: RESTORE REPORT ON PAGE REFRESH
// =======================================================

// Function to save the current dashboard state to browser memory
function saveDashboardState() {
    const reportContainer = document.getElementById('reportContainer');
    
    // Only save if the report is currently visible on the screen
    if (!reportContainer.classList.contains('hidden')) {
        const dashboardData = {
            daysInput: document.getElementById('days').value,
            statDays: document.getElementById('statDays').innerText,
            statReviews: document.getElementById('statReviews').innerText,
            aiReportHTML: document.getElementById('aiOutput').innerHTML
        };
        
        // Safely extract Chart.js data if a chart exists
        const chartId = Object.keys(Chart.instances)[0]; // Grab the active chart ID
        if (chartId) {
            const chart = Chart.instances[chartId];
            dashboardData.chartLabels = chart.data.labels;
            dashboardData.chartDatasets = chart.data.datasets;
        }

        // Save the compiled data object to sessionStorage as a JSON string
        sessionStorage.setItem('savedDashboard', JSON.stringify(dashboardData));
    }
}

// Event listener to automatically restore data when the page reloads (e.g., hitting F5)
window.addEventListener('load', function() {
    const savedDataStr = sessionStorage.getItem('savedDashboard');
    
    if (savedDataStr) {
        const data = JSON.parse(savedDataStr);
        
        // Restore input values, text statistics, and AI HTML content
        document.getElementById('days').value = data.daysInput;
        document.getElementById('statDays').innerText = data.statDays;
        document.getElementById('statReviews').innerText = data.statReviews;
        document.getElementById('aiOutput').innerHTML = data.aiReportHTML;
        
        // Unhide the main report container
        document.getElementById('reportContainer').classList.remove('hidden');
        
        // Re-draw the Chart with the saved dataset
        if (data.chartLabels && data.chartDatasets) {
            
            // Destroy any existing chart instance before restoring the saved chart
            let oldChart = Chart.getChart("sentimentChart");
            if (oldChart) {
                oldChart.destroy();
            }

            // Render the restored chart on the canvas
            const ctx = document.getElementById('sentimentChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.chartLabels,
                    datasets: data.chartDatasets
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { stepSize: 1 }
                        }
                    }
                }
            });
        }
    }
});

// Smart Observer: Watches the AI Output area and auto-saves whenever new content is injected
const observer = new MutationObserver(function() {
    saveDashboardState();
});

// Start watching the 'aiOutput' element for any structural changes (e.g., when a new report generates)
observer.observe(document.getElementById('aiOutput'), { childList: true, subtree: true });