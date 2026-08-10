import './title.css';
import homeImg from '../../assets/homeImg.gif';

function Title() {
  return (
    <header className="hero">
      <div className="hero-inner">
        <div className="hero-content">
          <div className="hero-image">
            <img src={homeImg} alt="Data visualization" />
          </div>
          <div className="hero-text">
            <h1 className="hero-title">Data API Platform</h1>
            <p className="hero-subtitle">
              Discover, query, and integrate high-quality datasets with a single,
              developer-friendly API. Fast access, consistent schemas, and secure
              delivery — so your team can build faster.
            </p>

            <div className="hero-ctas">
              <a className="btn btn-primary" href="/datasets">Get started</a>
              
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Title;