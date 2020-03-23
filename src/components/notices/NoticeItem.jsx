import React, { Component } from "react";
import "../../styles/friends-notices-search/NoticeItem.scss";
import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

class NoticeItem extends Component {
  constructor(props) {
    super(props);
    this.props = props;
  }


  render() {
    const {
      username, userID, type, handleAccept, handleDecline,
    } = this.props;
    return (
      <Row className="wrapper">
        <Col md={12} lg={4} className="leftColumn">
          <Link
            to={{
              pathname: `/profile/${username}`,
              state: { username, userID },
            }}
            className="username-link"
          >
            {username}
          </Link>
        </Col>
        <Col md={12} lg={3} className="middleColumn">
          <div className="type-wrapper">Local</div>
        </Col>
        <Col md={12} lg={5} className="rightColumn">
          <div className="button-wrapper">
            <button type="button" className="accept-button" onClick={() => handleAccept(userID)}>Accept</button>
            <button type="button" className="decline-button" onClick={() => handleDecline(userID)}>Decline</button>
          </div>
        </Col>
      </Row>
    );
  }
}

NoticeItem.propTypes = {
  username: PropTypes.string.isRequired,
  userID: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
  handleAccept: PropTypes.func.isRequired,
  handleDecline: PropTypes.func.isRequired,
};

export default NoticeItem;
