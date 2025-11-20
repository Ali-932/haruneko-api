import NodeRemoteProcedureCallContract from './node/RemoteProcedureCallContract';

export interface IRemoteProcedureCallContract {
    LoadMediaContainerFromURL(url: string): Promise<void>;
}

export function CreateRemoteProcedureCallContract(): IRemoteProcedureCallContract {
    // API-only mode: always use Node RPC contract
    return new NodeRemoteProcedureCallContract();
}