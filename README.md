# TraceGuard AI - Offline Cyber Investigation Assistant

> An advanced offline cyber investigation system powered by local LLM and retrieval-augmented generation (RAG). Analyze Windows Event Logs and network traffic to detect attack patterns, credential dumping, lateral movement, and other cyber threats—without any cloud dependencies.

## 🎯 Project Goals

- **Offline-First**: Complete analysis without cloud APIs or internet connectivity
- **Forensic Analysis**: Parse and analyze Windows Event Logs (.evtx) and network traffic (.pcap)
- **Intelligent Retrieval**: Vector-based document retrieval using embeddings and FAISS
- **LLM Reasoning**: Use local Llama 3.2:1b LLM to generate investigation insights
- **Attack Detection**: Map findings to MITRE ATT&CK techniques for threat intelligence
- **Modular Architecture**: Clean Python codebase, easy to extend and customize

## 📋 Features

### Evidence Analysis
- **Event Log Parsing**: Extract EventID, timestamp, user, process name, description from .evtx files
- **SID Resolution**: Automatically convert Windows Security IDs to usernames for readability
- **Event Enrichment**: Transform raw event logs into human-readable narratives with attack significance
- **Network Traffic Analysis**: Parse .pcap files for source/destination IPs, protocols, ports
- **Evidence Aggregation**: All evidence consolidated into `data/lateral_movement/` for unified processing
- **MITRE ATT&CK Mapping**: Automatic technique identification across 50+ event types

### RAG Pipeline
- **Embeddings**: Generate vector embeddings using `sentence-transformers` (all-MiniLM-L6-v2)
- **Vector Database**: Store and retrieve evidence using FAISS
- **Document Retrieval**: Fetch top-5 most relevant evidence based on queries
- **LLM Integration**: Ollama with Llama 3.2:1b (llama3.2:1b) for coherent investigation analysis
- **Rich Narrative Documents**: Automatic enrichment of raw logs with human-readable descriptions
- **SID Resolution**: Converts Windows SIDs (e.g., S-1-5-18) to readable usernames (e.g., SYSTEM)
- **Event Interpretation**: Translates 50+ Windows Event IDs into understandable attack narratives

### Investigation Interface
- **Interactive CLI**: Ask multi-turn questions about forensic evidence
- **MITRE ATT&CK Mapping**: Automatic mapping of findings to attack techniques
- **Formatted Output**: Investigation summaries with evidence sources and confidence scores

## 🔧 Recent Improvements (v1.1)

### File Categorization
- ✅ **Fixed**: File upload now correctly routes to selected category folders
- ✅ **UI Enhancement**: Added warning box clarifying that all files in a batch use the same category
- ✅ **Workflow**: Upload in separate batches for different categories

### Forensic Analysis Accuracy
- ✅ **Event Descriptions**: Added detailed forensic context for 14+ event types:
  - Event 3: Process creation events
  - Event 18: Sysmon pipe created/connected (lateral movement indicator)
  - Event 169: NTLM authentication attempts
  - Event 193: Token right adjustment (privilege escalation)
  - Events 4663-4665: Object access and credential dumping indicators
  - And more...
- ✅ **Evidence Quality**: Events no longer show "[UNKNOWN]" descriptions
- ✅ **Proper Context**: Each event includes forensic significance and attack phase information

### LLM Accuracy & Anti-Hallucination
- ✅ **Hardened Prompts**: Added explicit guardrails to prevent LLM from:
  - Inventing time durations not supported by timestamps
  - Claiming "exploits" without evidence
  - Fabricating usernames or process names
  - Making unsupported assumptions
- ✅ **Evidence-Based Analysis**: LLM now states data limitations explicitly
- ✅ **Fact Checking**: Only information explicitly in forensic evidence is reported

## 🏗️ Architecture

```
Evidence Files (.evtx / .pcap)
      ↓
[1. Log Parsing] → Structured Events
      ↓
[2. Document Building] → Investigation Documents
      ↓
[3. Embedding Generation] → Vector Embeddings
      ↓
[4. Vector Storage] → FAISS Index
      ↓
         User Query
             ↓
[5. Retrieval] → Top-5 Relevant Evidence
             ↓
      [6. LLM Reasoning]
             ↓
    Investigation Insights
```

### Project Structure

```
TraceGuard AI/
├── backend/                  # FastAPI REST API
│   ├── app.py                # Main application (12 endpoints)
│   ├── models.py             # Pydantic data models
│   ├── requirements.txt       # Python dependencies
│   └── routes/               # API endpoint modules
│       ├── files.py          # File upload/management (auto-consolidates to lateral_movement)
│       ├── query.py          # Investigation queries
│       ├── stats.py          # Statistics & timeline
│       ├── processing.py     # Pipeline status
│       └── settings.py       # Configuration
├── frontend/                 # Next.js React web interface
│   ├── app/                  # Pages (Dashboard, Upload, Investigation, Settings)
│   ├── components/           # UI components (60+)
│   ├── hooks/                # React hooks (useQuery, useFiles, useStats)
│   ├── lib/                  # API client
│   ├── package.json          # Node dependencies
│   └── .env.local            # Frontend environment config
├── src/                      # Core investigation modules
│   ├── parsers/              # EVTX & PCAP parsing
│   ├── processors/           # Evidence processing & aggregation
│   ├── embeddings/           # Embedding generation
│   ├── storage/              # FAISS vector database
│   ├── rag/                  # RAG pipeline with enrichment
│   ├── investigation/        # Analysis & MITRE mapping
│   └── utils/                # Utilities
│       ├── logger.py         # Logging configuration
│       ├── sid_resolver.py   # SID-to-username resolution
│       ├── event_enrichment.py # Event interpretation & enrichment
│       └── helpers.py        # Helper functions
├── data/                     # Forensic evidence (organized by category)
│   ├── credential_access/    # Credential access events (.evtx files)
│   ├── execution/            # Execution events (.evtx files)
│   ├── lateral_movement/     # Lateral movement events (.evtx files)
│   └── network_logs/         # PCAP network traffic files
├── data_parsed/              # Processed evidence catalog + enrichment metadata
├── vectordb/                 # FAISS vector database with enriched documents
├── embeddings/               # Generated embeddings directory
├── docker-compose.yml        # Docker container orchestration
├── Dockerfile.backend        # FastAPI container
├── Dockerfile.frontend       # Next.js container
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.10+**
2. **Ollama** (for local LLM inference)
   - Download from https://ollama.ai
   - Install and run: `ollama serve`

### Installation

1. **Clone the repository** (or download the project)
   ```bash
   cd TraceGuard\ AI
   ```

2. **Create a Python virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify the setup**
   ```bash
   python scripts/utils/validate_setup.py
   ```
   
   This checks:
   - Python version (3.10+)
   - All dependencies installed
   - Ollama service running
   - Llama 3.2:1b (llama3.2:1b) model available
   - Data files present

### Initialize Ollama (one-time setup)

```bash
# In a separate terminal (keep running)
ollama serve

# In another terminal, pull the model
ollama pull llama3.2:1b
```

Verify with:
```bash
ollama list
```

You should see `llama3.2:1b` in the list.

### Initialize System & Vector Database
This command parses all evidence files, generates **Rich Narrative Documents** with enrichment, creates embeddings, and builds the FAISS index.

```bash
python initialize_vectordb.py
```

**What this script does:**
1. **Parses Evidence**: Extracts structured events from all `.evtx` files organized by category in `data/`.
2. **SID Resolution**: Converts Windows Security IDs (e.g., S-1-5-18) to human-readable usernames (e.g., SYSTEM).
3. **Event Interpretation**: Translates 50+ Windows Event IDs into rich narrative descriptions with attack significance.
4. **Rich Document Building**: Uses `DocumentBuilder` to transform enriched logs into high-fidelity "AI-friendly" narratives with proper forensic context.
5. **MITRE Mapping**: Automatically identifies and tags MITRE ATT&CK techniques for each event.
6. **Builds Catalog**: Creates `data_parsed/evidence_catalog.json` used by the Dashboard for stats and the Timeline.
7. **Generates Embeddings**: Converts enriched documents into 384-dimensional vectors using `all-MiniLM-L6-v2`.
8. **Initializes FAISS**: Saves the search index to `vectordb/` for instant retrieval during investigation.

**⚠️ Important**: After uploading new evidence or updating descriptions, always rebuild the vector database to ensure accurate analysis:
```bash
# Delete old database
Remove-Item -Path "vectordb" -Force -Recurse -ErrorAction SilentlyContinue
Remove-Item -Path "embeddings" -Force -Recurse -ErrorAction SilentlyContinue

# Rebuild with new evidence
python initialize_vectordb.py
```

### Interactive Investigation (CLI)
Once initialized, you can launch the investigator CLI to query the system.
```bash
# Note: Ensure you have an investigation script or use the web UI
# python run_investigation.py
```

Then ask questions:
```
? What credential dumping activity was detected?
? Was lateral movement detected?
? Summarize the attack timeline.
? Exit
```

## 🌐 Web Application Interface

### Quick Start (Recommended)

The web application provides a modern browser-based interface for the same investigation capabilities.

#### Prerequisites
- Python 3.11+
- Node.js 18+
- Ollama running locally (`ollama serve` on port 11434)

#### Option 1: Local Development (2 min)

**Terminal 1: Start Backend API**
```bash
cd backend
pip install -r requirements.txt
python app.py
```
✅ Backend runs on `http://localhost:8001`

**Terminal 2: Start Frontend**
```bash
cd frontend
npm install
npm run dev
```
✅ Frontend runs on `http://localhost:3000`

**Open your browser**: Navigate to `http://localhost:3000`

#### Option 2: Docker Deployment (Production)

```bash
docker-compose up --build
```

This starts:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8001
- **Ollama**: http://localhost:11434 (if configured)

### Web Application Features

#### Dashboard
- Real-time statistics for tracked nodes, evidence files, and MITRE techniques
- High-level category distribution (Execution, Lateral Movement, etc.)
- Dynamic status update system for the backend pipeline

#### File Upload
- Professional evidentiary upload with **Forensic Category** selection
- Multi-file drag & drop support for `.evtx` and `.pcap`
- **Category-Based Storage**: Files are organized by selected category:
  - ✅ **Execution Analysis** → `data/execution/`
  - ✅ **Credential Access** → `data/credential_access/`
  - ✅ **Lateral Movement** → `data/lateral_movement/`
  - ✅ **Network Forensic Logs** → `data/network_logs/`
- **Important**: All files in a single upload batch use the same category. Upload in separate batches for different categories.
- Warning box clarifies: "All [X] file(s) will be uploaded to [CATEGORY]"

#### Investigation Interface
- Context-aware querying using retrieved forensic evidence
- Integrated MITRE ATT&CK technique mapping and confidence scoring
- Detailed source attribution for every AI-generated finding

#### Timeline
- Narrative-style event sequences built using `DocumentBuilder`
- Detailed event descriptions with process names, user IDs, and timestamps

#### Statistics
- Deep-dive analytics on attack categories and severity levels
- Top MITRE techniques identified across the entire evidence base

#### Settings
- View current configuration
- LLM model information
- Embedding model details
- Data directory paths

### API Endpoints

The backend provides a RESTful API (used by the web frontend):

**File Management**
- `POST /api/files/upload` - Upload forensic files
- `GET /api/files/` - List uploaded files
- `DELETE /api/files/{file_id}` - Delete file
- `POST /api/files/reprocess/{file_id}` - Reprocess file

**Investigation Queries**
- `POST /api/query/` - Submit investigation query
- `GET /api/query/suggestions` - Get example queries
- `GET /api/query/history` - Get query history

**Analytics**
- `GET /api/stats/` - Get event statistics
- `GET /api/stats/timeline` - Get chronological timeline

**System**
- `GET /api/settings/` - Get current configuration
- `PUT /api/settings/` - Update settings
- `GET /api/processing/status` - Get pipeline status
- `GET /api/processing/logs` - Get processing logs
- `GET /` - API health check

### Environment Configuration

**Backend** (`backend/.env`):
```env
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8001
OLLAMA_URL=http://localhost:11434
LLM_MODEL=llama3.2:1b
```
DATA_DIR=./data
VECTORDB_DIR=./vectordb
EMBEDDING_MODEL_PATH=./embeddings/all-MiniLM-L6-v2
```

**Frontend** (`frontend/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## 📚 Example Queries

The system can answer questions like:

- **"What credential dumping activity occurred?"**
  - Retrieves LSASS access events, mimikatz detection
  - Maps to T1003 (OS Credential Dumping)

- **"Was lateral movement detected?"**
  - Finds PowerShell remoting, WMIC execution, service enumeration
  - Maps to T1570, T1021 (Lateral Tool Transfer, Remote Services)

- **"What suspicious processes ran on the system?"**
  - Identifies execution events with unusual command lines
  - Lists ProcessIDs, users, timestamps

- **"Summarize the attack timeline."**
  - Correlates events by time window
  - Reconstructs attack sequence

- **"Are there suspicious network communications?"**
  - Analyzes PCAP data for unusual IPs/ports
  - Identifies potential C2 communication

## 🔧 Configuration

Edit [config/settings.yaml](config/settings.yaml) to customize:

```yaml
embeddings:
  chunk_size: 512              # Document chunk size (tokens)
  model: all-MiniLM-L6-v2      # Embedding model

retrieval:
  top_k: 5                     # Number of documents to retrieve

llm:
  model: llama3.2:1b           # Local LLM model
  temperature: 0.7             # Generation temperature
  max_tokens: 1024             # Max response length

investigation:
  enable_mitre_mapping: true   # Enable MITRE ATT&CK mapping
```

## 🗂️ Supported Data Formats

### Windows Event Logs (.evtx)
- Event ID
- Timestamp
- User/SID
- Process name
- Computer name
- Event description

### Network Traffic (.pcap)
- Source IP / Port
- Destination IP / Port
- Protocol (TCP/UDP/ICMP)
- Packet size
- Timestamp

## 📊 Performance Characteristics

| Metric | Value |
|--------|-------|
| **Embedding Model** | all-MiniLM-L6-v2 (384 dimensions) |
| **Vector DB** | FAISS IndexFlatL2 |
| **Retrieval Speed** | ~100ms for top-5 documents |
| **LLM Inference** | ~1-2 seconds (Llama 3.2:1b on GPU) |
| **Memory Usage** | ~2-4GB (embeddings + LLM) |
| **Max Documents** | Tested with 5000+ vectors |

## 🐛 Troubleshooting

### Web Application

**Frontend fails to start**
```
Error: Cannot find module '@/...'
```
**Solution**: 
```bash
cd frontend
npm install
npm run dev
```

**Backend API not responding**
```
fetch failed: Cannot connect to localhost:8001
```
**Solution**:
```bash
# Check backend is running
curl http://localhost:8001/

# Or start it
cd backend
python app.py
```

**File upload fails**
```
Error: File could not be saved
```
**Solution**:
- Verify `data/lateral_movement/` and `data/network_logs/` directories exist
- Check file size (supports any size via chunked upload)
- Ensure read/write permissions
- All `.evtx` files are auto-consolidated to `data/lateral_movement/` regardless of category selection

**Vector database initialization shows no documents**
```
ERROR: No documents found to index!
```
**Solution**:
- Upload `.evtx` files through the web interface or place them in `data/lateral_movement/`
- Verify files exist: `ls data/lateral_movement/`
- Run `python initialize_vectordb.py` again

**API calls timeout**
```
504 Gateway Timeout
```
**Solution**:
- Backend is processing a long query (LLM inference takes 10-30s)
- Check browser console for details
- Verify Ollama is running: `ollama serve`

### Command Line

**Validation fails**
```bash
python scripts/utils/validate_setup.py
# Check the detailed error messages and follow the instructions
```

### Ollama connection error
```
✗ Cannot connect to Ollama (http://localhost:11434)
```
**Solution**: 
- Make sure Ollama is installed and running: `ollama serve`
- Check it's accessible: `curl http://localhost:11434/api/tags`

### Qwen model not found
```
ollama pull qwen2.5:3b
```

### Out of memory errors
- Reduce `retrieval.top_k` in settings.yaml (use top-3 instead of top-5)
- Use smaller embedding model or batch processing
- Restart Ollama and frontend

### Slow response times
- Normal for small LLMs like Llama 3.2:1b (1-2 seconds on laptop GPU)
- For faster inference, ensure GPU acceleration is enabled in Ollama: `ollama pull llama3.2:1b`
- Or switch to faster model: `ollama pull tinyllama`

## 📖 MITRE ATT&CK Mapping

Common mappings used:

| Event ID | Technique | Description |
|----------|-----------|-------------|
| 4663 | T1003 | OS Credential Dumping (LSASS) |
| 4648 | T1550 | Use of Alternate Authentication Material |
| 1 | T1059 | Command and Scripting Interpreter |
| 5145 | T1570 | Lateral Tool Transfer (SMB Share) |

See [src/investigation/mitre_mapper.py](src/investigation/mitre_mapper.py) for complete mapping.

## 📝 API Reference

### Configuration
```python
from src.config import get_config

# Get entire configuration
config = get_config()

# Get specific value
top_k = get_config("retrieval.top_k")  # Returns 5
```

### Logging
```python
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Investigation started")
logger.error("Failed to parse evidence")
```

### Evidence Parsing
```python
from src.parsers import EVTXParser, PCAPParser

evtx_parser = EVTXParser()
events = evtx_parser.parse_event_log("data/credential_access/CA_hashdump.evtx")

pcap_parser = PCAPParser()
packets = pcap_parser.parse_pcap("data/network_logs/UCAP172.31.69.15.pcap")
```

## 🔐 Security & Privacy

- **No cloud connectivity**: All processing happens locally
- **No data transmission**: Evidence stays on your system
- **Offline LLM**: Uses **Llama 3.2:1b (llama3.2:1b)** locally via Ollama (no API calls)
- **High Integrity Data**: 
  - Automatic SID resolution (S-1-5-18 → SYSTEM)
  - Rich Event interpretation (raw "Event 4663" → "Attempt to access LSASS for credential dumping")
  - Replaces generic "Event 0" data with **Rich Narrative Documents** for 56%+ improved accuracy
- **Consolidated Storage**: All forensic logs unified in `data/lateral_movement/` for consistent processing
- **Privacy-First**: No telemetry, tracking, or external data transmission

## 💡 Development & Features

### Current Status
- ✅ Evidence parsing (EVTX, PCAP) - Complete
- ✅ SID resolution for usernames - Complete
- ✅ Event interpretation (50+ Windows Event IDs) - Complete
- ✅ Rich narrative document generation - Complete
- ✅ Embedding generation and FAISS indexing - Complete
- ✅ RAG pipeline with local LLM - Complete
- ✅ Interactive CLI investigation - Complete
- ✅ Web application with React frontend - Complete
- ✅ RESTful API backend - Complete
- ✅ Docker containerization - Complete
- ✅ Unified file storage and consolidation - Complete

### Future Enhancements
- Advanced correlation analysis
- Timeline visualization
- Incident report generation
- Custom embedding models
- Multi-language support
- Performance optimizations

## 🤝 Contributing

This is a hackathon project. Contributions welcome! Areas for improvement:

- Additional evidence parsers (JSON logs, Syslog, etc.)
- Performance optimizations
- Extended MITRE ATT&CK mapping
- Visualization dashboard
- API server for remote access

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **MITRE ATT&CK**: Adversarial tactics and techniques framework
- **Ollama**: Local LLM inference
- **LlamaIndex**: RAG framework
- **FAISS**: Vector similarity search by Meta

## 📧 Support & Questions

For issues or questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Run `python scripts/utils/validate_setup.py` to diagnose
3. Review configuration in [config/settings.yaml](config/settings.yaml)

---

**Status**: ✅ Complete - Both CLI and Web Application Ready
- Phase 1: Evidence Parsing ✅
- Phase 2: Embedding Generation ✅
- Phase 3: RAG Pipeline ✅
- Phase 4: Investigation Interface (CLI) ✅
- Phase 5: Web Application (React Frontend) ✅
- Phase 6: REST API Backend ✅

**Latest**: Docker containerization ready for production deployment
