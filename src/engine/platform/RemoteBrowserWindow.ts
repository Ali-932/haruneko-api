import type { IObservable } from '../Observable';
import { Observable } from '../Observable';
import type { ScriptInjection } from './FetchProviderCommon';

export interface IRemoteBrowserWindow {
    get DOMReady(): IObservable<void, IRemoteBrowserWindow>;
    get BeforeWindowNavigate(): IObservable<URL, IRemoteBrowserWindow>;
    get BeforeFrameNavigate(): IObservable<URL, IRemoteBrowserWindow>;
    Open(request: Request, show: boolean, preload: ScriptInjection<void>): Promise<void>;
    Close(): Promise<void>;
    Show(): Promise<void>;
    Hide(): Promise<void>;
    /**
     * Evaluate the given {@link script} and return the result from the last instruction.
     */
    ExecuteScript<T extends void | JSONElement>(script: ScriptInjection<T>): Promise<T>;
    /**
     * Send chrome debug protocol commands.
     * @see https://chromedevtools.github.io/devtools-protocol/1-3/
     */
    SendDebugCommand<T extends void | JSONElement>(method: string, parameters?: JSONObject): Promise<T>;
}

/**
 * Stub implementation for API mode (not used - Puppeteer is used instead)
 */
class StubRemoteBrowserWindow implements IRemoteBrowserWindow {
    private _domReady = new Observable<void, IRemoteBrowserWindow>(undefined as any);
    private _beforeWindowNavigate = new Observable<URL, IRemoteBrowserWindow>(undefined as any);
    private _beforeFrameNavigate = new Observable<URL, IRemoteBrowserWindow>(undefined as any);

    get DOMReady(): IObservable<void, IRemoteBrowserWindow> {
        return this._domReady;
    }
    get BeforeWindowNavigate(): IObservable<URL, IRemoteBrowserWindow> {
        return this._beforeWindowNavigate;
    }
    get BeforeFrameNavigate(): IObservable<URL, IRemoteBrowserWindow> {
        return this._beforeFrameNavigate;
    }
    async Open(request: Request, show: boolean, preload: ScriptInjection<void>): Promise<void> {
        // No-op in API mode
    }
    async Close(): Promise<void> {
        // No-op in API mode
    }
    async Show(): Promise<void> {
        // No-op in API mode
    }
    async Hide(): Promise<void> {
        // No-op in API mode
    }
    async ExecuteScript<T extends void | JSONElement>(script: ScriptInjection<T>): Promise<T> {
        // No-op in API mode
        return undefined as T;
    }
    async SendDebugCommand<T extends void | JSONElement>(method: string, parameters?: JSONObject): Promise<T> {
        // No-op in API mode
        return undefined as T;
    }
}

export function CreateRemoteBrowserWindow(): IRemoteBrowserWindow {
    // API-only mode: return stub implementation (Puppeteer is used instead)
    return new StubRemoteBrowserWindow();
}