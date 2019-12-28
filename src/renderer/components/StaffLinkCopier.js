import React, { useState } from "react";
import $ from "jquery";

import { isStaff, login, useAuthData } from "../utils/auth.js";
import LinkCopier from "./LinkCopier.js";
import ModalButton from "./ModalButton.js";

export default function StaffLinkCopier({ fileData }) {
    const authData = useAuthData();

    const defaultStaffLink = "Authorizing...";
    const [staffLink, setStaffLink] = useState(defaultStaffLink);

    if (authData.loggedOut) {
        return (
            <ModalButton buttonText="Log in" onClick={login}>
            You must log in as course staff to share code with students.
            </ModalButton>
        );
    } else if (isStaff(authData)) {
        if (staffLink === defaultStaffLink) {
            $.post("/api/staff_share", fileData).done(link => setStaffLink(link));
        }
        return (
            <LinkCopier link={staffLink}>
                Share the following link with your students to let them access your code.
            </LinkCopier>
        );
    } else {
        return null;
    }
}
