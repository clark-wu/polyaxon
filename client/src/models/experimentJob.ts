import { LastFetchedNames } from './utils';

export class ExperimentJobModel {
  public uuid: string;
  public unique_name: string;
  public pod_id: string;
  public name: string;
  public id: number;
  public role: string;
  public last_status: string;
  public experiment: number;
  public definition: string;
  public deleted?: boolean;
  public project?: string;
  public status?: string;
  public created_at: string;
  public updated_at: string;
  public started_at: string;
  public finished_at: string;
  public node_scheduled: string;
  public resources: { [key: string]: any };
}

export class ExperimentJobStateSchema {
  public byUniqueNames: { [uniqueName: string]: ExperimentJobModel };
  public uniqueNames: string[];
  public lastFetched: LastFetchedNames;
}

export const ExperimentJobsEmptyState = {
  byUniqueNames: {},
  uniqueNames: [],
  lastFetched: new LastFetchedNames()
};
