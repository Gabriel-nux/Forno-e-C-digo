export type HalfHalfState = { a: string; b: string };

export type HalfHalfAction = { type: "sabor-a"; id: string } | { type: "sabor-b"; id: string };

export function estadoInicial(
  ids: readonly string[],
  preferidos: readonly [string, string],
): HalfHalfState {
  const [pa, pb] = preferidos;
  if (pa !== pb && ids.includes(pa) && ids.includes(pb)) return { a: pa, b: pb };
  const [a, b] = ids;
  if (a === undefined || b === undefined || a === b)
    throw new Error("o meio a meio precisa de ao menos dois sabores distintos");
  return { a, b };
}

// "Os dois sabores são diferentes" é decidido aqui e em mais nenhum lugar.
// Se a pessoa escolhe num lado o sabor que já está no outro, os lados trocam em vez de dar erro.
export function halfHalfReducer(state: HalfHalfState, action: HalfHalfAction): HalfHalfState {
  switch (action.type) {
    case "sabor-a":
      return { a: action.id, b: action.id === state.b ? state.a : state.b };
    case "sabor-b":
      return { b: action.id, a: action.id === state.a ? state.b : state.a };
  }
}

export function precoMeioAMeio(precoA: number, precoB: number): number {
  return Math.max(precoA, precoB);
}
