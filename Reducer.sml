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