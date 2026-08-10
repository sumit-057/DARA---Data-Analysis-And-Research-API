import './App.css';
import Features from './components/Features/Features.jsx';
import Footer from './components/Footer/Footer.jsx';
import Navbar from './components/Navbar/Navbar.jsx';
import Title from './components/Title/title.jsx';

function App() {
  return (
    <div className="App">
      <Navbar />
      <Title />
      <Features />
      <Footer />
    </div>
  );
}

export default App;