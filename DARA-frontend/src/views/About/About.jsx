import './About.css';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';

function AboutPage() {
  return (
    <div className="about-page-root">
      <Navbar />
      <div className="about-page">
        <div className="about-header">
          <h1>About Us</h1>
          <p>Learn more about our data platform and mission</p>
        </div>

        <div className="about-container">
          <section className="about-section">
            <h2>Our Mission</h2>
            <p>
              We believe that quality data analytics should be accessible to everyone. Our platform makes it easy for developers and businesses to discover, query, and integrate high-quality datasets through a single, developer-friendly API.
            </p>
          </section>

          <section className="about-section">
            <h2>What We Offer</h2>
            <ul>
              <li>✓ Well-structured analyzed APIs for datasets</li>
              <li>✓ Fast and reliable RESTful APIs</li>
              <li>✓ Comprehensive documentation</li>
            </ul>
          </section>

          <section className="about-section">
            <h2>Our Technology</h2>
            <p>
              Built with modern technologies including Python, Pandas for data processing, and a robust REST API architecture.
            </p>
          </section>

          <section className="about-section">
            <h2>Get Started Today</h2>
            <p>
              Join thousands of developers who are building amazing applications with our data API platform. Start today and experience the difference quality data makes.
            </p>
            <a href="/datasets"><button className="btn btn-primary">Start Here</button></a>
          </section>
        </div>
      </div>
      <Footer />
    </div>
  );
}

export default AboutPage;
