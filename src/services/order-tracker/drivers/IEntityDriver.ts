import { TWithStringIds } from '@/services/mongo/TWithStringIds';
import { ObjectId } from 'mongodb';

export type TGeoCoordinates = [number, number];

export interface IGeoPoint {
  type: 'Point';
  coordinates: TGeoCoordinates;
}

export interface IEntityDriver {
  _id: ObjectId;
  home_location_point: IGeoPoint;
  available_status: true;
  driving_radius_miles: number;
}

export type TEntityDriverClient = TWithStringIds<IEntityDriver>;
