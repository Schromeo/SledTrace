import type { LlmUsageCall } from "./usage";

export type TextTokenRate = {
  inputPerMillion: number;
  cachedInputPerMillion: number;
  outputPerMillion: number;
  sourceUrl: string;
};

// Official OpenAI Standard text-token prices checked 2026-09-24.
// This is an indicative snapshot, not billing data or a live price feed.
export const OPENAI_STANDARD_TEXT_RATES: Readonly<Record<string, TextTokenRate>> = {
  "gpt-4.1-mini": {
    inputPerMillion: 0.4, cachedInputPerMillion: 0.1, outputPerMillion: 1.6,
    sourceUrl: "https://developers.openai.com/api/docs/models/gpt-4.1-mini",
  },
  "gpt-4.1-mini-2025-04-14": {
    inputPerMillion: 0.4, cachedInputPerMillion: 0.1, outputPerMillion: 1.6,
    sourceUrl: "https://developers.openai.com/api/docs/models/gpt-4.1-mini",
  },
  "gpt-4o-mini": {
    inputPerMillion: 0.15, cachedInputPerMillion: 0.075, outputPerMillion: 0.6,
    sourceUrl: "https://developers.openai.com/api/docs/models/gpt-4o-mini",
  },
  "gpt-4o-mini-2024-07-18": {
    inputPerMillion: 0.15, cachedInputPerMillion: 0.075, outputPerMillion: 0.6,
    sourceUrl: "https://developers.openai.com/api/docs/models/gpt-4o-mini",
  },
};

export type CostEstimate = { usd: number; sourceUrl: string; priceDate: string };

export function formatEstimatedUsd(usd: number): string {
  if (usd > 0 && usd < 0.000001) return "<$0.000001 USD";
  return `$${usd.toFixed(6)} USD`;
}

export function estimateOpenAITextCost(
  call: LlmUsageCall,
  rates: Readonly<Record<string, TextTokenRate>> = OPENAI_STANDARD_TEXT_RATES,
): CostEstimate | null {
  if (call.provenance !== "openai_responses" || call.total.kind !== "known" ||
      call.inputTokens.kind !== "known" || call.outputTokens.kind !== "known" ||
      call.cachedInputTokens.kind !== "known" ||
      call.cacheWriteTokens.kind !== "known" || call.cacheWriteTokens.value !== 0) {
    return null;
  }
  const rate = rates[call.model];
  if (!rate || call.cachedInputTokens.value > call.inputTokens.value) return null;
  if (![rate.inputPerMillion, rate.cachedInputPerMillion, rate.outputPerMillion]
    .every((value) => Number.isFinite(value) && value >= 0)) return null;
  const input = call.inputTokens.value - call.cachedInputTokens.value;
  const usd = (input * rate.inputPerMillion +
    call.cachedInputTokens.value * rate.cachedInputPerMillion +
    call.outputTokens.value * rate.outputPerMillion) / 1_000_000;
  return { usd, sourceUrl: rate.sourceUrl, priceDate: "2026-09-24" };
}
