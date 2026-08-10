import './Datasets.css';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import datasets from './data';

function DatasetsPage() {
	const [selected, setSelected] = useState(null);

		// datasets imported from ./data

	return (
		<div className="datasets-root">
			<Navbar />

			<main className="datasets-page">
				<header className="datasets-header">
					<h1>Datasets</h1>
					<p>Explore curated, cleaned datasets available through our API endpoints.</p>
				</header>

				<section className="datasets-container">
					<div className="datasets-grid">
									{datasets.map((d) => (
										<article key={d.id} className="dataset-card" onClick={() => setSelected(d)}>
								<div className="dataset-icon">{d.icon}</div>
								<h3>{d.name}</h3>
								<p className="dataset-description">{d.description}</p>
								<div className="dataset-meta">
									<h5>📊 {d.records.toLocaleString()} records</h5>
									<h5 className="data-updated">🕐 {d.updated}</h5>
								</div>
								<div className="dataset-tags">
									{d.tags.map((t, i) => (<span className="tag" key={i}>{t}</span>))}
								</div>
											<Link to={`/datasets/${d.id}`} className="btn btn-primary">View API Docs</Link>
							</article>
						))}
					</div>
				</section>

				{selected && (
					<div className="modal-overlay" onClick={() => setSelected(null)}>
						<div className="modal-content" onClick={(e) => e.stopPropagation()}>
							<button className="close-btn" onClick={() => setSelected(null)}>✕</button>
							<div className="modal-icon">{selected.icon}</div>
							<h2>{selected.name}</h2>
							<p>{selected.description}</p>
							<div className="modal-meta">
								<div><strong>Total Records:</strong> {selected.records.toLocaleString()}</div>
								<div><strong>Last Updated:</strong> {selected.updated}</div>
							</div>
							<div className="modal-tags">
								{selected.tags.map((t,i) => <span className="tag" key={i}>{t}</span>)}
							</div>
							<button className="btn btn-primary">Get Started with API</button>
						</div>
					</div>
				)}
			</main>

			<Footer />
		</div>
	);
}

export default DatasetsPage;

