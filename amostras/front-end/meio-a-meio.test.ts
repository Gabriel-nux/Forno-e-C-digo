import { describe, expect, it } from "vitest";
import { estadoInicial, halfHalfReducer, type HalfHalfState } from "./meio-a-meio";

const inicio: HalfHalfState = { a: "calabresa", b: "pepperoni" };

describe("halfHalfReducer", () => {
  it("troca um sabor sem mexer no outro", () => {
    expect(halfHalfReducer(inicio, { type: "sabor-a", id: "mms" })).toEqual({
      a: "mms",
      b: "pepperoni",
    });
  });

  it("escolher no lado A o sabor do lado B troca os lados", () => {
    expect(halfHalfReducer(inicio, { type: "sabor-a", id: "pepperoni" })).toEqual({
      a: "pepperoni",
      b: "calabresa",
    });
  });

  it("nunca deixa os dois sabores iguais, em qualquer sequência de ações", () => {
    const ids = ["calabresa", "pepperoni", "mms", "napolitana"];
    let estado = inicio;
    for (let i = 0; i < 200; i++) {
      const id = ids[(i * 7 + 3) % ids.length]!;
      estado = halfHalfReducer(
        estado,
        i % 2 === 0 ? { type: "sabor-a", id } : { type: "sabor-b", id },
      );
      expect(estado.a).not.toBe(estado.b);
    }
  });
});

describe("estadoInicial", () => {
  it("cai para os dois primeiros quando o par preferido não existe ou é repetido", () => {
    expect(estadoInicial(["a", "b", "c"], ["x", "y"])).toEqual({ a: "a", b: "b" });
    expect(estadoInicial(["a", "b", "c"], ["a", "a"])).toEqual({ a: "a", b: "b" });
  });

  it("recusa menos de dois sabores", () => {
    expect(() => estadoInicial(["a"], ["a", "b"])).toThrow();
  });
});
