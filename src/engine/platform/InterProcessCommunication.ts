export type Callback = (...parameters: JSONArray) => Promise<void>;

export interface IPC<TChannelsOut extends string, TChannelsIn extends string> {
    Listen(channel: TChannelsIn, callback: Callback): void;
    Send<T extends void | JSONElement>(channel: TChannelsOut, ...parameters: JSONArray): Promise<T>;
}

/**
 * Stub IPC implementation for API mode (no GUI IPC needed)
 */
class StubIPC implements IPC<string, string> {
    Listen(channel: string, callback: Callback): void {
        // No-op in API mode
    }
    async Send<T extends void | JSONElement>(channel: string, ...parameters: JSONArray): Promise<T> {
        // No-op in API mode
        return undefined as T;
    }
}

let instance: IPC<string, string>;

export default function GetIPC() {
    if(!instance) {
        instance = new StubIPC();
    }
    return instance;
}