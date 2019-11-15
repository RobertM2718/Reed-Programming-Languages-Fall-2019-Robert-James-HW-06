datatype
    Term = 
    Lam  of string * Term
  | Juxt of Term   * Term
  | Name of string

(*
Various printing functions.
*)
fun prettyString (Lam (s, t)) ks    = let val space = (ks^"   | ") in let val lev = (ks^"   +-") in
                                      "Lam+-"^s^"\n"^space^"\n"^lev^(prettyString t (ks^"     ")) end end
  | prettyString (Juxt (t1, t2)) ks = let val space = (ks^"   | ") in let val lev = (ks^"   +-") in
                                      "App+-"^(prettyString t1 space)^"\n"^space^"\n"^lev^(prettyString t2 (ks^"     ")) end end
  | prettyString (Name s) ks        = "Var "^s

fun ppTerm t = print (prettyString t "")

fun uString (Lam (s, t))    = "Lam ("^s^", "^(uString t)^")"
  | uString (Juxt (t1, t2)) = "App ("^(uString t1)^", "^(uString t2)^")"
  | uString (Name s)        = "(Var "^s^")"

fun upTerm t = print (uString t)


local
(*
Helper functions for the reducers
*)
    val count = ref ~1
    
    fun isNumChar c = String.isSubstring (String.str c) ("0123456789")
    
    fun stripID nil = nil
      | stripID (#"_"::(x::xs)) = if (isNumChar x) then nil
                                      else #"_"::(stripID (x::xs))
      | stripID (x :: xs) = x :: (stripID xs)
(*
Produces a fresh variable from the base of an older one, assumes any _(digit) occurs after the end of the base, if at all.
*)
    fun newVar var = (count := !count + 1;
          (implode (stripID (explode var)))^"_"^(Int.toString (!count)))

    fun setminus nil y = nil
      | setminus (l::ls) y = if (y = l) then (setminus ls y) else (l :: (setminus ls y))

    fun pushdown y nil = (y :: nil)
      | pushdown y (l::ls) = if (y = l) then (y :: ls) else (l :: (pushdown y ls))

    fun union nil ls = ls
      | union (y::ys) ls = (union ys (pushdown y ls))

    fun contains nil y = false
      | contains (l::ls) y = if y = l then true else contains ls y

    fun freeVar (Name (s)) = s::nil
      | freeVar (Lam (s,t)) = (setminus (freeVar t) s)
      | freeVar (Juxt (t1, t2)) = (union (freeVar t1) (freeVar t2))

    fun subst s x (Name (v)) = if v = x then s else (Name (v))
      | subst s x (Lam (v, t)) = if v = x then Lam (v, t)
                            else if contains (freeVar s) v then let val vp = newVar v
                                                                in (subst s x (Lam (vp, (subst (Name vp) v t)))) end
                            else Lam (v, (subst s x t))
      | subst s x (Juxt (t1, t2)) = Juxt ((subst s x t1), (subst s x t2))


    datatype reduxOption = SOME of Term
                         | NONE


    fun findBetaRedux (Name s) = NONE
      | findBetaRedux (Lam (v, t)) = findBetaRedux t
      | findBetaRedux (Juxt (Lam (v, t1), t2)) = SOME (Juxt (Lam (v, t1), t2))
      | findBetaRedux (Juxt (t1, t2)) = case (findBetaRedux t1) of SOME t => SOME t
                                                                 | NONE   => findBetaRedux t2

    fun reduceStep t = case t of Name s => NONE
                               | Lam (v, t) => (case reduceStep t of NONE   => NONE
                                                                   | SOME p => SOME (Lam (v, p)))
                               | Juxt (Lam (v, t1), t2) => SOME (subst t2 v t1)
                               | Juxt (t1, t2) => (case reduceStep t1 of SOME p => SOME (Juxt (p, t2))
                                                                       | NONE   => (case reduceStep t2 of SOME p2 => SOME (Juxt (t1, p2))
                                                                                                        | NONE    => NONE))
in
(*
Normal-order reducers for Terms, they all use the same basic structure and differ in how they print, except for bddReduce which is limited to n steps of reduction.
*)
    fun reduce t = case reduceStep t of NONE   => t
                                      | SOME p => reduce p

    fun ppReduce t = (print "\n ########## \n"; ppTerm t; case reduceStep t of NONE   => (print "\n ########## \n"; t)
                                                                             | SOME p => ppReduce p)
    fun upReduce t = (print "\n ########## \n"; upTerm t; case reduceStep t of NONE   => (print "\n ########## \n"; t)
                                                                             | SOME p => upReduce p)

    fun bddReduce t n = if n < 1 then t else case reduceStep t of NONE => t
                                                                | SOME p => bddReduce p (n-1)
end
