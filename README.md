# 🌐 Global Supply Chain Disruption Dashboard

A comprehensive Streamlit dashboard that monitors and analyzes global supply chain disruptions through real-time news analysis, impact assessment, and geographic visualization.

![Dashboard Preview](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## 🚀 Features

### 📰 **News Category View**
- **10+ Categories**: Natural Disasters, Geopolitical, Transportation, Economic Crisis, etc.
- **Smart Filtering**: Filter by news sources and categories
- **Impact Assessment**: Automated impact level scoring (High/Medium/Low)
- **Real-time Updates**: Fresh news every 30 minutes

### 🌍 **Geo-Location View**
- **Interactive World Map**: Click countries to see related disruptions
- **Country-specific News**: Filter articles by geographic location
- **Supply Chain Hotspots**: Visual identification of affected regions

### ⚡ **AI-Powered Analysis**
- **Entity Recognition**: Identifies critical companies, ports, and countries
- **Impact Scoring**: Weighted algorithm considering keywords, entities, and scope
- **LLM Integration**: Optional GPT analysis for deeper insights
- **Smart Caching**: Optimized performance with dual-layer caching

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- NewsAPI account (free tier available)
- Optional: OpenAI API key for enhanced analysis

### Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Supply_Chain_Disruption_Dashboard.git
   cd Supply_Chain_Disruption_Dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

3. **Configure API keys**
   ```bash
   # Create api_keys.py file
   echo "NEWSAPI_KEY = 'your_newsapi_key_here'" > api_keys.py
   echo "OPENAI_API_KEY = 'your_openai_key_here'" >> api_keys.py  # Optional
   ```

4. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

## 📋 Requirements

Core dependencies from `requirements.txt`:
- `streamlit` - Web dashboard framework
- `requests` - API communication
- `spacy` - Natural Language Processing
- `plotly` - Interactive visualizations
- `pandas` - Data manipulation
- `openai` - Optional AI analysis

## 🎯 Usage

### Getting Started
1. Launch the dashboard: `streamlit run app.py`
2. Choose between **News Category View** or **Geo-Location View**
3. Filter by categories, sources, or geographic regions
4. Click article titles for detailed analysis

### View Types

#### 📰 News Category View
- Browse by disruption type (Natural Disasters, Geopolitical, etc.)
- Filter articles by trusted news sources
- See impact assessments and country mentions

#### 🌍 Geo-Location View
- Interactive world map showing affected countries
- Click countries to see location-specific news
- Geographic distribution of supply chain risks

## 🧠 Impact Assessment Algorithm

The dashboard uses a sophisticated weighted scoring system:

```python
# Weighted Impact Calculation
final_score = (
    keyword_score * 0.30 +      # 30% - Scale & scope keywords
    entity_score * 0.35 +       # 35% - Critical entities (companies, ports)
    criticality_score * 0.20 +  # 20% - Disruption severity
    geographic_score * 0.15     # 15% - Geographic scope
)
```

### Impact Levels
- 🔴 **High Impact** (7.0+): Major global disruptions
- 🟡 **Medium Impact** (4.0-6.9): Regional or moderate disruptions  
- 🟢 **Low Impact** (<4.0): Minor or local disruptions

## 📊 Data Sources

- **NewsAPI**: 30+ trusted news sources including Reuters, Bloomberg, BBC
- **Entity Recognition**: spaCy NLP for company/location identification
- **Geographic Data**: Country mappings for visualization
- **Caching**: Local storage for performance optimization

## 🔧 Architecture

```
Supply_Chain_Disruption_Dashboard/
├── app.py                     # Main Streamlit dashboard
├── data_fetcher.py           # News API integration & caching
├── impact_assessment.py      # Impact scoring algorithms
├── country_extraction.py     # Geographic analysis
├── LLM_Article_Analysis.py   # Optional AI analysis
├── data_filtering.py         # Article filtering utilities
├── requirements.txt          # Python dependencies
└── Testing_scripts/          # Unit tests
```

## 🚦 Performance Features

- **Dual-Layer Caching**: File + memory caching for optimal speed
- **Smart Loading**: Progressive loading with status indicators
- **API Optimization**: Efficient NewsAPI usage within rate limits
- **Error Handling**: Graceful fallbacks for network issues

## 🧪 Testing

Run the included test scripts:
```bash
python Testing_scripts/test_impact_assessment.py
python Testing_scripts/test_llm_analysis.py
python Testing_scripts/test_weighted_scoring.py
```

## 📈 Future Enhancements

- [ ] Real-time alerts for high-impact disruptions
- [ ] Historical trend analysis
- [ ] Supply chain vulnerability mapping
- [ ] Export functionality for reports
- [ ] Mobile-responsive design

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhancement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/enhancement`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NewsAPI** for reliable news data
- **spaCy** for NLP capabilities
- **Streamlit** for the dashboard framework
- **Plotly** for interactive visualizations

## 📞 Support

For issues or questions:
- Create an issue on GitHub
- Check the [Wiki](../../wiki) for documentation
- Review the `backlog.txt` for known issues

---

**Built with ❤️ for supply chain professionals and analysts**
