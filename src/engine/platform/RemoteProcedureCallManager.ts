import type { SettingsManager } from '../SettingsManager';
import NodeRemoteProcedureCallManager from './node/RemoteProcedureCallManager';

export interface IRemoteProcedureCallManager {
    Stop(): Promise<void>;
    Restart(port: number, secret: string): Promise<void>;
}

export function CreateRemoteProcedureCallManager(settingsManager: SettingsManager): IRemoteProcedureCallManager {
    // API-only mode: always use Node RPC manager
    return new NodeRemoteProcedureCallManager();
}