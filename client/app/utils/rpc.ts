import type { DateTime } from "luxon";
import type { RfcToBe } from "~/purple_client";

export type CookedDraft = Omit<RfcToBe, 'externalDeadline'> & {
  externalDeadline: DateTime<false> | DateTime<true> | null
}
