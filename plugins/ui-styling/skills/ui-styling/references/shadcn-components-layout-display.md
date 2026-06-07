# shadcn/ui: Layout, Data, and Feedback Components

## Card

```tsx
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card Description</CardDescription>
  </CardHeader>
  <CardContent><p>Card Content</p></CardContent>
  <CardFooter><Button>Action</Button></CardFooter>
</Card>
```

## Tabs

```tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

<Tabs defaultValue="account">
  <TabsList>
    <TabsTrigger value="account">Account</TabsTrigger>
    <TabsTrigger value="password">Password</TabsTrigger>
  </TabsList>
  <TabsContent value="account">Account settings</TabsContent>
  <TabsContent value="password">Password settings</TabsContent>
</Tabs>
```

## Accordion

```tsx
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"

<Accordion type="single" collapsible>
  <AccordionItem value="item-1">
    <AccordionTrigger>Is it accessible?</AccordionTrigger>
    <AccordionContent>Yes. It adheres to WAI-ARIA design pattern.</AccordionContent>
  </AccordionItem>
</Accordion>
```

## Toast

```tsx
import { useToast } from "@/hooks/use-toast"
const { toast } = useToast()
toast({ title: "Scheduled: Catch up", description: "Friday at 5:57 PM" })
```

## Alert

```tsx
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

<Alert><AlertTitle>Heads up!</AlertTitle><AlertDescription>You can add components using CLI.</AlertDescription></Alert>
<Alert variant="destructive"><AlertTitle>Error</AlertTitle><AlertDescription>Session expired.</AlertDescription></Alert>
```

## Progress and Skeleton

```tsx
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"

<Progress value={33} />
<Skeleton className="h-12 w-12 rounded-full" />
<Skeleton className="h-4 w-[250px]" />
```

## Table

```tsx
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

<Table>
  <TableCaption>Recent invoices</TableCaption>
  <TableHeader>
    <TableRow><TableHead>Invoice</TableHead><TableHead>Status</TableHead></TableRow>
  </TableHeader>
  <TableBody>
    <TableRow><TableCell>INV001</TableCell><TableCell>Paid</TableCell></TableRow>
  </TableBody>
</Table>
```

## Avatar and Badge

```tsx
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"

<Avatar>
  <AvatarImage src="https://github.com/shadcn.png" />
  <AvatarFallback>CN</AvatarFallback>
</Avatar>
<Badge>Default</Badge>
<Badge variant="secondary">Secondary</Badge>
<Badge variant="destructive">Destructive</Badge>
```
