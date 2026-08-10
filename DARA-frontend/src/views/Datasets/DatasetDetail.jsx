import './Datasets.css';
import { useParams, Link } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import datasets from './data';

function DatasetDetail() {
  const { id } = useParams();
  const dataset = datasets.find((d) => String(d.id) === String(id));

  if (!dataset) {
    return (
      <div>
        <Navbar />
        <main style={{padding:40}}>
          <h2>Dataset not found</h2>
          <p>The dataset you requested does not exist.</p>
          <Link to="/datasets" className="btn btn-primary">Back to Datasets</Link>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div>
      <Navbar />
      <main className="datasets-page">
        <div className="datasets-container" style={{maxWidth:900}}>
          <div style={{display:'flex',gap:20,alignItems:'center',marginBottom:12}}>
            <div className="modal-icon">{dataset.icon}</div>
            <div>
              <h1 style={{margin:0}}>{dataset.name}</h1>
              <p style={{margin:0,color:'#6b7280'}}>Last updated: {dataset.updated}</p>
            </div>
          </div>

          <p style={{color:'#4b5563'}}>{dataset.description}</p>

          <div className="modal-meta">
            <div><strong>Total Records:</strong> {dataset.records.toLocaleString()}</div>
            <div><strong>Tags:</strong> {dataset.tags.join(', ')}</div>
          </div>

          <div style={{display:'flex',gap:12,marginTop:16}}>
            <Link to="/documentation" className="btn btn-primary">View API Docs</Link>
            <button onClick={() => window.history.back()} className="btn back-btn">Back</button>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}

export default DatasetDetail;
