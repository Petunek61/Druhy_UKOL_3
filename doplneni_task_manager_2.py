import mysql.connector
from mysql.connector import Error

def pripojeni_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="19611966",
            database="ukoly_db"
        )
        return connection
    except Error as e:
        print(f"Chyba při připojení: {e}")
        return None


def vytvoreni_tabulky(connection):
    try:
        cursor = connection.cursor()
        # 1. Vytvoření tabulky, pokud neexistuje
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ukoly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev VARCHAR(255) NOT NULL COLLATE utf8mb4_bin CHECK (nazev <> ''),
            popis TEXT NOT NULL CHECK (popis <> ''),
            stav ENUM('nezahájeno', 'hotovo', 'probíhá') DEFAULT 'nezahájeno',
            datum_vytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
      # 2. Zjištění, zda už omezení na popis existuje
        cursor.execute("""
        SELECT CONSTRAINT_NAME
        FROM information_schema.TABLE_CONSTRAINTS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'ukoly'
          AND CONSTRAINT_TYPE = 'CHECK'
          AND CONSTRAINT_NAME = 'chk_popis_neprazdny';
        """)

        exists = cursor.fetchone()

        # 3. Pokud omezení neexistuje, pokusíme se ho přidat
        if not exists:
            try:
                cursor.execute("""
                ALTER TABLE ukoly
                ADD CONSTRAINT chk_popis_neprazdny CHECK (popis <> '');
                """)
                print("Omezení pro neprázdný popis bylo úspěšně přidáno.")
            except Error as e:
                print(f"Nelze přidat omezení pro popis: {e}")
        else:
            print("Omezení chk_popis_neprazdny již existuje.")

        print("Tabulka úkoly byla úspěšně vytvořena nebo již existovala.")

    except Error as e:
        print(f"Chyba při vytváření tabulky: {e}")  


def pridat_ukol(connection):
    try:
        nazev = input("Zadejte název úkolu: ").strip()
        popis = input("Zadejte popis úkolu: ").strip()

        if not nazev:
            print("Chyba: Název úkolu nesmí být prázdný!")
            return

        if not popis:
            print("Chyba: Popis úkolu nesmí být prázdný!")
            return      

        pridat_ukol_db(connection, nazev, popis)
        print("Úkol byl úspěšně přidán.")
    except Error as e:
        print(f"Chyba při přidávání úkolu: {e}")

def pridat_ukol_db(connection, nazev, popis):
            
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO ukoly (nazev, popis)
        VALUES (%s, %s)
        """, (nazev, popis))
    connection.commit()
            
                

def zobrazit_ukoly(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("""
        SELECT id, nazev, popis, stav, datum_vytvoreni
        FROM ukoly
        WHERE stav IN ('nezahájeno', 'probíhá')
        """)
        rows = cursor.fetchall()
        
        if rows:
            print("\nSeznam úkolů:")
            for row in rows:
                print(f"ID: {row[0]}, Název: {row[1]}, Popis: {row[2]}, Stav: {row[3]}, Datum vytvoření: {row[4]}")
        else:
            print("Seznam úkolů je prázdný.")
    except Error as e:
        print(f"Chyba při zobrazování úkolů: {e}")

def aktualizovat_ukol(connection):
    try:
        zobrazit_ukoly(connection)
        id_ukolu = input("Zadejte ID úkolu, který chcete aktualizovat: ").strip()
        
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM ukoly WHERE id = %s", (id_ukolu,))
        existuje = cursor.fetchone()[0]
        
        if existuje == 0:
            print("Úkol s tímto ID neexistuje. Zkuste to znovu.")
            return
        
        novy_stav = input("Zadejte nový stav ('probíhá', 'hotovo'): ").strip()
        
        if novy_stav not in ('probíhá', 'hotovo'):
            print("Neplatný stav, zkuste to znovu.")
            return
        
        aktualizovat_ukol_db(connection, novy_stav, id_ukolu)
        print("Úkol byl úspěšně aktualizován.")
    
    except Error as e:
        print(f"Chyba při aktualizaci úkolu: {e}")


def aktualizovat_ukol_db(connection, novy_stav, id_ukolu):
    
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE ukoly
        SET stav = %s
        WHERE id = %s
        """, (novy_stav, id_ukolu))
    connection.commit()
    


def odstranit_ukol(connection):
    try:
        zobrazit_ukoly(connection)
        id_ukolu = input("Zadejte ID úkolu, který chcete odstranit: ").strip()
        
        pocet = odstranit_ukol_db(connection, id_ukolu)
        
        if pocet > 0:
            print("Úkol byl úspěšně odstraněn.")
        else:
            print("Úkol s tímto ID neexistuje.")
    except Error as e:
        print(f"Chyba při odstraňování úkolu: {e}")

def odstranit_ukol_db(connection, id_ukolu):
    
    cursor = connection.cursor()
    cursor.execute("""
        DELETE FROM ukoly
        WHERE id = %s
        """, (id_ukolu,))
    connection.commit()
    return cursor.rowcount    

def hlavni_menu(connection):
    while True:
        print("\nHlavní nabídka:")
        print("1. Přidat úkol")
        print("2. Zobrazit úkoly")
        print("3. Aktualizovat úkol")
        print("4. Odstranit úkol")
        print("5. Ukončit program")
        
        volba = input("Vyberte možnost: ")
        
        if volba == "1":
            pridat_ukol(connection)
        elif volba == "2":
            zobrazit_ukoly(connection)
        elif volba == "3":
            aktualizovat_ukol(connection)
        elif volba == "4":
            odstranit_ukol(connection)
        elif volba == "5":
            print("Program ukončen.")
            connection.close()
            break
        else:
            print("Neplatná volba, zkuste to znovu.")

if __name__ == "__main__":
    conn = pripojeni_db()
    
    if conn:
        vytvoreni_tabulky(conn)
        hlavni_menu(conn)
    else:
        print("Nepodařilo se připojit k databázi.")
