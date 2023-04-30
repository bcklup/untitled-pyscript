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

  const logger = useCallback(
    (text) => {
      setLogs((prevLogs) => `${prevLogs}\n${text}`);
      console.log("[Log] logRel", { logRef });
      if (logRef && logRef.current) {
        logRef.current.scrollTop = logRef.current?.scrollHeight;
      }
    },
    [setLogs, logRef]
  );

  useEffect(() => {
    const hostIP = window.location.hostname;
    try {
      const ioSocket = io.connect(`http://${hostIP}:5000`);

      if (ioSocket.connected) {
        ioSocket.on("temp", (data) => {
          setTemperatureValue(data.temp);
        });

        ioSocket.on("log", (data) => {
          logger(data.log);
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

        setSocket(ioSocket);
      } else {
        ioSocket.disconnect();
        throw new Error();
      }
    } catch (e) {
      logger(
        `[${new Date().toLocaleTimeString()}][ERR] Error establishing connection...`
      );
      if (socket) socket.disconnect();
      console.log(e);
    }
    return () => {
      if (socket) socket.disconnect();
    };
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
        socket.emit("stage2_response_trigger", true);
      } else {
        socket.emit("stage2_response_trigger", false);
      }
    },
    [socket]
  );

  const handleClearLogs = useCallback(() => {
    setLogs("");
  }, [setLogs]);

  const handleRestart = useCallback(() => {
    handleClearLogs();
    setState(STATES.SETUP);
  }, [handleClearLogs]);

  return (
    <div className="bg-zinc-500 h-screen w-full items-center justify-center flex flex-1">
      <div className="flex flex-col bg-white shadow-lg h-full w-11/12 md:w-[768px]">
        <div className="flex flex-row w-full p-3 bg-slate-700 items-center justify-between">
          <p className="font-light text-white">
            Connection:{" "}
            <span
              className={twMerge(
                "font-semibold",
                socket !== null ? "text-emerald-400" : "text-red-400"
              )}
            >
              {socket !== null ? "Active" : "Inactive"}
            </span>
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
          <div className="mt-3 md:mt-24">
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
              <p className="text-xl">Start Stage 1?</p>
              <div className="flex flex-row space-x-4">
                <button
                  className="font-bold text-white bg-green-400 px-5 py-1 rounded-sm"
                  onClick={handleStartStage1}
                >
                  Start
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
                  onClick={handleStartStage2(true)}
                >
                  Yes
                </button>
                <button
                  className="font-bold text-white bg-red-400 px-6 py-2 rounded-sm"
                  onClick={handleStartStage2(false)}
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
                  onClick={handleStartStage2(true)}
                >
                  Yes
                </button>
                <button
                  className="font-bold text-white bg-red-400 px-6 py-2 rounded-sm"
                  onClick={handleStartStage2(false)}
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
