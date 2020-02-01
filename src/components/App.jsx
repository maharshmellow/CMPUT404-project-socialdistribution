import React from "react";
import "../styles/App.scss";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import PostBlock from "./PostBlock";

function App() {
  return (
    <Container fluid className="app">
      <PostBlock />
    </Container>
  );
}

export default App;
