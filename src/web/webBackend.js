import {
    CLAIM_MENU, ERR, EXIT,
    INTERACT_PROCESS,
    KILL_PROCESS,
    OPEN_FILE, OUT, REGISTER_OKPY_HANDLER, SAVE_FILE,
    SHOW_OPEN_DIALOG, SHOW_SAVE_DIALOG
} from "../common/communicationEnums.js";
import { PYTHON, SCHEME } from "../common/languages.js";
import python from "../languages/python/web/communication.js";
import { interactProcess, killProcess } from "../main/processes.js";
import { assignMenuKey } from "./webMenuHandler.js";
// import scheme from "../languages/scheme/communication.js";

let handler;

const webBackend = {
    send: (messageType, message) => {
        receive(message);
    },
    on: (messageType, handlerArg) => {
        handler = handlerArg;
    },
};

export default webBackend;

function receive(arg) {
    console.log("Receive", arg);
    if (!arg.handler) {
        // main server handler
        if (arg.type === INTERACT_PROCESS) {
            interactProcess(arg.key, arg.line);
        } else if (arg.type === KILL_PROCESS) {
            killProcess(arg.key);
        } else if (arg.type === CLAIM_MENU) {
            assignMenuKey(arg.key);
        } else {
            console.error(`Unknown (or missing) type: ${arg.type}`);
        }
    } else if (arg.handler === PYTHON) {
        python(arg);
    } else {
        console.error(`Unknown handler: ${arg.handler}`);
    }
}

export function send(arg) {
    console.log("Send", arg);
    handler(null, arg);
}

export function out(key, val) {
    send({ key, type: OUT, out: val });
}

export function err(key, val) {
    send({ key, type: ERR, out: val });
}

export function exit(key, val) {
    send({ key, type: EXIT, out: val });
}

export function sendAndExit(key, msg) {
    out(key, msg);
    exit(key);
}
