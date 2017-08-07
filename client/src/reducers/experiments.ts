import {Reducer} from "redux";

import {ExperimentAction, actionTypes} from "../actions/experiment";
import {ExperimentModel} from "../models/experiment";

export const experimentsReducer: Reducer<{byIds: {[id: number]: ExperimentModel}, ids: number[]}> =
	(state: {byIds: {[id: number]: ExperimentModel}, ids: number[]} = {
    byIds: {10: {id: 10, name: 'name1'}, 20: {id: 20, name: 'name2'}},
    ids: [10, 20]
	}, action: ExperimentAction) => {

  switch (action.type) {
    case actionTypes.CREATE_EXPERIMENT:
      return {
        ...state,
        byIds: {...state.byIds, [action.experiment.id] : experiment},
        ids: [...state.ids, action.experiment.id]
      };
    case actionTypes.DELETE_EXPERIMENT:
      return {
        ...state,
        byIds: {...state.byIds, [action.experimentId] : {...state.byIds[action.experimentId], delete:true}},
        ids: state.ids.filter(id => id != action.experimentId),
      };
    case actionTypes.UPDATE_EXPERIMENT:
      return {
        ...state,
        byIds: {...state.byIds, [action.experiment.id]: action.experiment}
      };
    case actionTypes.RECEIVE_EXPERIMENTS:
      var newState = {...state};
      for (let xp of action.experiments) {
        if (!newState.ids.includes(xp.id)) {
          newState.ids.push(xp.id);
          newState.byIds[xp.id] = xp;
        }
      }
      return newState;
  }
  return state;
};
