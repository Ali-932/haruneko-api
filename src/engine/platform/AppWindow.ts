export interface IAppWindow {
    /**
     * Hide the application window and show the loading splash screen.
     */
    ShowSplash(): Promise<void>;
    /**
     * Show the application window and hide the loading splash screen.
     */
    HideSplash(): Promise<void>;
    readonly HasControls: boolean;
    Minimize(): void;
    Maximize(): void;
    Restore(): void;
    Close(): void;
}

/**
 * No-op function for API mode (no GUI to reload)
 */
export function ReloadAppWindow(force = false): void {
    // No-op in API mode - there's no window to reload
}