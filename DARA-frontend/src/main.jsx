import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import App from './App.jsx'
import AboutPage from './views/About/About.jsx'
import DatasetsPage from './views/Datasets/Datasets.jsx'
import DatasetDetail from './views/Datasets/DatasetDetail.jsx'
import Documentation from './views/Documentation/Documentation.jsx'

// Mount the React app into the #root element in index.html
const container = document.getElementById('root')
if (!container) throw new Error('Root container not found in index.html')

const root = createRoot(container)
root.render(
	<StrictMode>
		<BrowserRouter>
			<Routes>
				<Route path="/" element={<App />} />
				<Route path="/datasets" element={<DatasetsPage />} />
				<Route path="/datasets/:id" element={<DatasetDetail />} />
				<Route path="/about" element={<AboutPage />} />
				<Route path="/documentation" element={<Documentation />} />
			</Routes>
		</BrowserRouter>
	</StrictMode>
)


