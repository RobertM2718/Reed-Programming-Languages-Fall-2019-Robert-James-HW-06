datatype
    Term = 
    Lam  of string * Term
  | Juxt of Term   * Term
  | Name of string


local 
  val count = ref ~1
  
  fun isNumChar c = String.isSubstring (String.str c) ("0123456789")
  
  fun stripID nil = nil
    | stripID (#"_"::(x::xs)) = if (isNumChar x) then nil
                                    else #"_"::(stripID (x::xs))
    | stripID (x :: xs) = x :: (stripID xs)
  
in
  fun newVar var = (count := !count + 1;
        (implode (stripID (explode var)))^"_"^(Int.toString (!count)))
end

(*
fun reduce

and subst
  
and freeVar

*)
local
    fun setminus nil y = nil
      | setminus (l::ls) y = if (y = l) then (setminus ls y) else (l :: (setminus ls y))

    fun pushdown y nil = (y :: nil)
      | pushdown y (l::ls) = if (y = l) then (y :: ls) else (l :: (pushdown y ls))

    fun union nil ls = ls
      | union (y::ys) ls = (union ys (pushdown y ls))
in
    fun freeVar (Name (s)) = s::nil
      | freeVar (Lam (s,t)) = (setminus (freeVar t) s)
      | freeVar (Juxt (t1, t2)) = (union (freeVar t1) (freeVar t2))
end