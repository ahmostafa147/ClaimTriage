# Claims Triage Agent Pro 🚀

**A GUARANTEED hackathon-winning AI-powered claims processing system** featuring real-time streaming with Pathway, intelligent document extraction with LandingAI ADE, and transparent decision-making with evidence overlays.

## 🎯 Problem Statement

Insurance claims processing is a critical bottleneck in the industry, with manual triage leading to:
- **Delayed processing** (days to weeks)
- **Inconsistent routing** decisions
- **High operational costs** from manual review
- **Poor customer experience** due to delays
- **Fraud detection gaps** from human error

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React.js UI   │◄──►│   FastAPI        │◄──►│   Pathway       │
│   Frontend      │    │   Backend        │    │   Streaming     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   LandingAI ADE │
                       │   Document       │
                       │   Extraction     │
                       └──────────────────┘
```

### Key Components

- **🎨 React.js Frontend**: Modern, responsive UI with real-time updates
- **⚡ FastAPI Backend**: High-performance API with CORS support
- **🔄 Pathway Streaming**: Real-time data processing pipeline
- **🤖 LandingAI ADE**: Intelligent document extraction and OCR
- **📊 Metrics Dashboard**: Live performance monitoring
- **🔍 Evidence Overlay**: Visual highlighting of decision triggers
- **📈 Counterfactual Analysis**: What-if scenario testing
- **🧪 Backtesting**: Performance validation against gold labels

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for development)
- LandingAI API key

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ClaimTriage

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "LANDINGAI_API_KEY=your_api_key_here" > .env
```

### Running the System

```bash
# Start the backend server
source venv/bin/activate
python3 api.py

# The system will be available at http://localhost:8000
```

## 🎪 Demo Script (5 Minutes)

### 1. **Drop Suspicious Claim** (1 min)
- Upload a PDF with fraud keywords
- Watch it get instantly routed to `fraud_queue`
- Show evidence highlights on the PDF

### 2. **Edit Rule Threshold** (1 min)
- Change litigation threshold from $50k to $30k
- Watch existing claims reroute live with diff visualization
- Show counterfactual impact analysis

### 3. **Run Backtest** (1 min)
- Click "Run Backtest" button
- Show confusion matrix with precision/recall metrics
- Click on misclassified claims to investigate

### 4. **Show Real-time Metrics** (1 min)
- Point to metrics strip showing p50/p95 latencies
- Show queue sizes updating in real-time
- Demonstrate Pathway streaming processing

### 5. **Audit Trail** (1 min)
- Show SHA256 hashes for raw and structured data
- Demonstrate safety flags for low-confidence fields
- Show complete audit trail for compliance

## 🔧 Technology Stack

### Backend
- **Pathway**: Real-time streaming data processing
- **LandingAI ADE**: Document extraction and OCR
- **FastAPI**: High-performance web framework
- **Pydantic**: Data validation and serialization
- **PyMuPDF**: PDF processing and rendering

### Frontend
- **React.js**: Modern UI framework
- **Babel**: JavaScript transpilation
- **CSS3**: Modern styling and animations

### AI/ML
- **LandingAI ADE**: Intelligent document understanding
- **Custom Rule Engine**: Business logic evaluation
- **Confidence Scoring**: Field-level extraction confidence

## 📊 Features

### 🎯 Core Features
- **Real-time Processing**: Pathway streaming pipeline
- **Intelligent Extraction**: LandingAI ADE integration
- **Evidence Overlay**: Visual decision justification
- **Counterfactual Analysis**: What-if scenario testing
- **Backtesting**: Performance validation
- **Audit Trail**: Complete decision transparency

### 🚀 Wow Factors
- **Instant Fraud Detection**: Drop suspicious claim → routed to fraud
- **Live Rule Updates**: Edit threshold → watch claims reroute
- **Visual Evidence**: Highlight exact text that triggered rules
- **Performance Metrics**: Real-time latency and queue monitoring
- **Compliance Ready**: Full audit trail with SHA256 hashes

## 🔒 Safety & Compliance

### Audit Features
- **SHA256 Hashing**: Raw file and structured data integrity
- **Safety Flags**: Low-confidence field identification
- **Decision Transparency**: Complete rationale and evidence
- **Compliance Logging**: Full audit trail for regulators

### Error Handling
- **Graceful Degradation**: Fallback to mock mode on API failures
- **Input Validation**: Comprehensive data validation
- **Error Boundaries**: UI error containment
- **Retry Logic**: Robust API call handling

## 📈 Performance Metrics

The system tracks and displays:
- **Extraction Latency**: P50/P95 processing times
- **Routing Latency**: P50/P95 decision times
- **Queue Sizes**: Real-time queue monitoring
- **Throughput**: Claims processed per minute
- **Accuracy**: Precision, recall, F1 scores

## 🛠️ Development

### Project Structure
```
ClaimTriage/
├── api.py                 # FastAPI backend
├── index.html            # React frontend
├── pathway_pipe.py       # Pipeline orchestration
├── simple_pathway.py     # Pathway streaming pipeline
├── ade_client.py         # LandingAI ADE integration
├── rule_engine.py        # Business logic engine
├── schema.py             # Data models
├── metrics.py            # Performance tracking
├── counterfactual.py     # What-if analysis
├── enhanced_backtest.py  # Performance validation
└── requirements.txt      # Dependencies
```

### Key Files
- **`api.py`**: Main FastAPI server with all endpoints
- **`simple_pathway.py`**: Pathway streaming pipeline implementation
- **`ade_client.py`**: LandingAI ADE integration with fallback
- **`index.html`**: Complete React.js frontend application

## 🎯 LandingAI ADE Integration

The system uses LandingAI's Appliance Document Extractor (ADE) for:
- **Intelligent OCR**: High-accuracy text extraction
- **Structured Data**: Field-specific extraction
- **Confidence Scoring**: Per-field confidence levels
- **Bounding Boxes**: Precise location mapping
- **Table Extraction**: Complex table structure parsing

### ADE Configuration
```python
# API key configuration
os.environ["LANDINGAI_API_KEY"] = "your_api_key_here"

# Extraction fields
fields = [
    "claimant_name", "policy_id", "incident_date",
    "claim_amount", "injury_severity", "incident_type"
]
```

## 🔄 Pathway Streaming

Pathway provides real-time data processing capabilities:
- **Streaming Processing**: Continuous file monitoring
- **Real-time Updates**: Live UI updates
- **Scalable Architecture**: Handles high-volume processing
- **Fault Tolerance**: Robust error handling

### Pathway Pipeline
```python
# Real-time file processing
files_table = pw.io.fs.read(path=str(inbox_dir), format="binary")
claims_table = files_table.select(claim_data=extract_claim(...))
decisions_table = claims_table.select(decision_data=route_claim(...))
```

## 🧪 Testing

### Mock Mode
The system includes comprehensive mock data for development:
- **Synthetic PDFs**: Generated claim documents
- **Realistic Data**: Various claim types and scenarios
- **Performance Testing**: Latency and throughput simulation

### Production Mode
- **LandingAI ADE**: Real document extraction
- **Pathway Streaming**: Production-grade processing
- **Live Metrics**: Real performance monitoring

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For questions or support:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Built with ❤️ for hackathon success** 🏆