import React, { useState, useRef, useEffect, useCallback } from "react";
import io from "socket.io-client";
import { twMerge } from "tailwind-merge";
const STATES = {
  SETUP: "setup",
  READY: "ready",
  STAGE1: "stage1",
  STAGE1_PAUSE: "stage1_pause",
  STAGE1_PROMPT: "stage1_prompt",
  STAGE2: "stage2",
};

function App() {
  const [state, setState] = useState(STATES.SETUP);
  const [temperatureValue, setTemperatureValue] = useState(34);
  const [logs, setLogs] = useState("");
  const [socket, setSocket] = useState(null);
  const logRef = useRef(null);

  const logger = (text) => {
    setLogs((prevLogs) => `${prevLogs}\n${text}`);
    if (logRef && logRef.current) {
      logRef.current.scrollTop = logRef.current?.scrollHeight;
    }
  };

  useEffect(() => {
    connect();
    return () => {
      if (socket) socket.disconnect();
    };
  }, []);

  const connect = () => {
    try {
      const hostIP = window.location.hostname.toString();
      const ioSocket = io.connect(`${hostIP}:5000`);

      ioSocket.on("connect", (data) => {
        setSocket(ioSocket);
      });

      ioSocket.on("disconnect", (data) => {
        setSocket(null);
        setState(STATES.SETUP);
      });

      logger(
        `[CLIENT] Establishing connection to socket server (ws:${hostIP}:5001)`
      );

      ioSocket.on("temp", (data) => {
        setTemperatureValue(data);
      });

      ioSocket.on("log", (data) => {
        logger(data);
      });

      ioSocket.on("ready", () => {
        setState(STATES.READY);
      });

      ioSocket.on("restart", () => {
        handleRestart();
      });

      ioSocket.on("stage1_start", () => {
        setState(STATES.STAGE1);
      });

      ioSocket.on("stage1_prompt_cooling", () => {
        setState(STATES.STAGE1_PAUSE);
      });

      ioSocket.on("stage2_prompt_trigger", () => {
        setState(STATES.STAGE1_PROMPT);
      });

      ioSocket.on("stage2_start", () => {
        setState(STATES.STAGE2);
      });
    } catch (e) {
      logger(
        `[${new Date().toLocaleTimeString()}][ERR] Error establishing connection...`
      );
      if (socket) socket.disconnect();
      console.log(e);
    }
  };

  const handleReconnect = useCallback(() => {
    setState(STATES.SETUP);
    logger("[CLIENT] Reconnecting to socket server...");
    connect();
  }, []);

  const handleFullStop = useCallback(() => {
    socket.emit("abort");
  }, [socket]);

  const handleStartStage1 = useCallback(() => {
    socket.emit("stage1_trigger");
  }, [socket]);

  const handleContinueStage1 = useCallback(
    (answer) => () => {
      if (answer) {
        socket.emit("stage1_response_cooling", true);
      } else {
        socket.emit("stage1_response_cooling", false);
      }
    },
    [socket]
  );

  const handleStartStage2 = useCallback(
    (answer) => () => {
      if (answer) {
        socket.emit("stage2_response_trigger");
      } else {
        socket.emit("stage2_response_trigger");
      }
    },
    [socket]
  );

  const handleClearLogs = useCallback(() => {
    setLogs("");
  }, [setLogs]);

  const handleRestart = useCallback(() => {
    handleClearLogs();
    setState(STATES.READY);
  }, [handleClearLogs]);

  return (
    <div
      className="flex min-h-screen flex-1 flex-col items-center justify-center bg-zinc-500"
      style={{ minHeight: "100vh" }}
    >
      <div className="flex h-full flex-1 flex-col bg-white shadow-lg w-11/12 md:w-[768px]">
        <div className="flex flex-row w-full p-3 bg-slate-700 items-center justify-between">
          <p className="font-light text-white">
            Connection:{" "}
            {socket !== null ? (
              <span className="font-semibold text-emerald-400">Active</span>
            ) : (
              <button
                className="font-semibold text-red-400"
                onClick={handleReconnect}
              >
                Inactive
              </button>
            )}
          </p>
          <p className="font-light text-white">
            Host IP:{" "}
            <span className="font-semibold text-gray-400">
              {window.location.hostname}
            </span>
          </p>
        </div>
        <div className="flex flex-row w-full p-3 bg-teal-700 items-center justify-center">
          <p className="font-light text-white">
            Temperature:{" "}
            <span
              className={twMerge(
                "font-semibold text-2xl",
                temperatureValue > 80 ? "text-orange-600" : "text-white"
              )}
            >
              {temperatureValue}°C
            </span>
          </p>
        </div>
        {/* <button onClick={handleTurnOnRelays}>Turn On Relays</button>
      <button onClick={handleTurnOffRelays}>Turn Off Relays</button> */}
        <div className="flex flex-1 flex-col text-left items-left m-5">
          <div className="mt-3">
            <div className="flex flex-row justify-between items-end mb-2">
              <p>Program Log</p>
              <button
                className="font-bold text-white bg-slate-300 px-5 py-1.5 rounded-sm"
                onClick={handleClearLogs}
              >
                Clear
              </button>
            </div>
            <textarea
              ref={logRef}
              value={logs}
              rows={20}
              readOnly
              wrap="off"
              className="bg-stone-200 w-full px-3 font-mono text-sm"
            />
          </div>
          {state === STATES.READY && (
            <div className="flex flex-row w-full items-center justify-between bg-neutral-100 px-6 py-6">
              <p className="text-xl">Start</p>
              <div className="flex flex-row space-x-4">
                <button
                  className="font-bold text-white bg-green-400 px-5 py-1 rounded-sm"
                  onClick={handleStartStage1}
                >
                  Stage 1
                </button>
                <button
                  className="font-bold text-white bg-green-400 px-6 py-2 rounded-sm"
                  onClick={handleStartStage2}
                >
                  Stage 2
                </button>
              </div>
            </div>
          )}
          {state === STATES.STAGE1_PAUSE && (
            <div className="flex flex-row w-full items-center justify-between bg-neutral-100 px-6 py-6">
              <p className="text-xl">Continue?</p>
              <div className="flex flex-row space-x-4">
                <button
                  className="font-bold text-white bg-green-400 px-5 py-1 rounded-sm"
                  onClick={handleContinueStage1(true)}
                >
                  Yes
                </button>
                <button
                  className="font-bold text-white bg-red-400 px-6 py-2 rounded-sm"
                  onClick={handleContinueStage1(false)}
                >
                  No
                </button>
              </div>
            </div>
          )}
          {state === STATES.STAGE1_PROMPT && (
            <div className="flex flex-row w-full items-center justify-between bg-neutral-100 px-6 py-6">
              <p className="text-xl">Start Stage 2?</p>
              <div className="flex flex-row space-x-4">
                <button
                  className="font-bold text-white bg-green-400 px-5 py-1 rounded-sm"
                  onClick={handleStartStage2}
                >
                  Yes
                </button>
                <button
                  className="font-bold text-white bg-red-400 px-6 py-2 rounded-sm"
                  onClick={handleStartStage2}
                >
                  No
                </button>
              </div>
            </div>
          )}

          {[STATES.STAGE1, STATES.STAGE2].includes(state) && (
            <button
              className="font-bold text-white bg-red-500 px-6 py-3 rounded-md mt-8 sm:mt-28"
              onClick={handleFullStop}
            >
              FULL STOP MACHINE
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
