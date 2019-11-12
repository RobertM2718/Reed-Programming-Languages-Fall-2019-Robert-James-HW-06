datatype
    Term = 
    Lam  of String * Term
  | Juxt of Term   * Term
  | Name of String
  
