import "./Features.css"
import apiImg from "../../assets/api.png";
import schemaImg from "../../assets/schema.png";
import dataImg from "../../assets/data.png";
import docsImg from "../../assets/documentation.png";

export default function Features() {
  return (
    <section className="features">
      <h2>Why Use Our Platform?</h2>

      <div className="feature-grid">
        <div className="feature-card">
          <span ><img className="emoji" src={dataImg} alt="Data Analysis" /></span>
          <h3>Data Analysis</h3>
          <p>Get clean and structured insights extracted using Python and Pandas.</p>
        </div>

        <div className="feature-card">
          <span><img className="emoji" src={apiImg} alt="RESTful APIs" /></span>
          <h3>RESTful APIs</h3>
          <p>Access insights through fast and reliable JSON API endpoints.</p>
        </div>

        <div className="feature-card">
          <span ><img className="emoji" src={schemaImg} alt="Unified schema" /></span>
          <h3>Unified schema</h3>
          <p>Consistent, typed responses across endpoints</p>
        </div>

         <div className="feature-card">
          <span ><img className="emoji" src={docsImg} alt="API Documentation" /></span>
          <h3>API Documentation</h3>
          <p>Comprehensive and easy-to-use API documentation for all endpoints.</p>
        </div>

      </div>
    </section>
  );
}
