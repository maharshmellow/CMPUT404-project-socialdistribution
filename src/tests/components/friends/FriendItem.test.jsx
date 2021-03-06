import React from "react";
import { shallow } from "enzyme";
import FriendItem from "../../../components/friends/FriendItem";

describe("FriendItem Component", () => {
  it("should render correctly", () => {
    const component = shallow(<FriendItem
      user={{
        id: "", displayName: "", host: "", github: "", url: "",
      }}
      handleUnfollow={() => {}}
    />);
    expect(component).toMatchSnapshot();
  });
});
